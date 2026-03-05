# Core Parsing Logic for TXT Splitter | Optimized for bbbz123
import os
import re
from contextlib import contextmanager
from typing import Iterator, List, Dict, Any, Optional, Tuple, cast
import chardet # type: ignore

from core.patterns import get_language, detect_language
from core.document_loader import DocumentLoader, PreparedDocument
from core.mode_utils import (
    is_constraint_mode,
    is_line_mode,
    is_paragraph_mode,
    is_size_mode,
    is_word_mode,
    needs_secondary_constraint_chunking,
)

class TextParser:
    def __init__(self):
        self.document_loader = DocumentLoader()

    def prepare_document(self, file_path: str) -> PreparedDocument:
        """Prepare input document into normalized UTF-8 text."""
        return self.document_loader.prepare(file_path)

    def cleanup_prepared_document(self, doc: PreparedDocument) -> None:
        self.document_loader.cleanup(doc)

    def cleanup_all_prepared_documents(self) -> None:
        self.document_loader.cleanup_all()

    @contextmanager
    def prepared_document(self, file_path: str) -> Iterator[PreparedDocument]:
        """Context manager wrapper around prepare+cleanup lifecycle."""
        doc = self.prepare_document(file_path)
        try:
            yield doc
        finally:
            self.cleanup_prepared_document(doc)
    
    def detect_encoding(self, file_path):
        """
        Reads a chunk of the file to auto-detect its encoding.
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
                # Confidence check
                if result['confidence'] < 0.7 or not encoding:
                    # Fallback to general gbk or utf-8 based on common usage
                    return 'utf-8'
                
                # Handle gb2312/gbk mapping since gbk is a superset
                if encoding.lower() in ['gb2312', 'gb18030']:
                    return 'gbk'
                return encoding
        except Exception as e:
            raise Exception(f"Failed to detect encoding: {str(e)}")

    def analyze_structure(self, file_path: str, encoding: str = 'utf-8', lang: str = 'zh') -> str:
        """
        Deep Structural Analysis (Original Algorithm by bbbz123)
        Detect most probable hierarchical tokens based on frequency and nesting.
        """
        if lang == 'multi':
            return '卷,章'
            
        # If encoding is not provided, detect it
        if encoding == 'utf-8': # Default value, check if it was explicitly set or is still default
            detected_encoding = self.detect_encoding(file_path)
            if detected_encoding:
                encoding = detected_encoding

        # Read file content
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                lines: List[str] = f.readlines()
        except Exception:
            return 'Chapter' if lang == 'en' else '章'

        # Auto-detect language if not specified
        if lang == 'zh' or lang == 'auto': 
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                sample = f.read(50000)
            from core.patterns import detect_all_languages
            lang_ids = detect_all_languages(sample)
            lang = lang_ids[0] if lang_ids else 'zh'

        lang_config = get_language(lang)
        all_keywords = lang_config.structure_keywords
        keywords_map = lang_config.keywords_weight_map
        heading_re = lang_config.heading_regex
        toc_header_re = lang_config.toc_header_regex
        ones = lang_config.ones_set
        extract_fn = lang_config.extract_heading

        toc_start = -1
        for i, line in enumerate(lines[:500]):  # type: ignore
            if toc_header_re.search(line.strip()):
                toc_start = i + 1
                break

        seq: List[Tuple[str, str, int]] = []
        if toc_start >= 0:
            blank_streak: int = 0
            long_non_heading_streak: int = 0
            for idx, line in enumerate(cast(List[str], lines[toc_start:toc_start + 5000])):
                text = line.strip()
                if not text:
                    blank_streak += 1
                    if blank_streak > 5:
                        break
                    continue
                blank_streak = 0
                if len(text) > 120:
                    continue
                
                m = heading_re.search(text)
                if m:
                    long_non_heading_streak = 0
                    kw, num_str = extract_fn(m)
                    if kw:
                        toc_idx: int = toc_start + idx  # type: ignore[operator]
                        seq.append((kw, num_str, toc_idx))
                else:
                    if len(text) > 50:
                        long_non_heading_streak += 1  # type: ignore[operator]
                        if long_non_heading_streak >= 3:
                            break

        if not seq:
            for idx, line in enumerate(cast(List[str], lines[0:3000])):
                text = line.strip()
                if text and len(text) <= 80:
                    m = heading_re.search(text)
                    if m:
                        kw, num_str = extract_fn(m)
                        if kw:
                            seq.append((kw, num_str, idx))

        found_kws = list(dict.fromkeys(item[0] for item in seq))
        if not found_kws:
            return 'Chapter' if lang == 'en' else '章'

        # Count 'reset' parent-child relationships
        votes: Dict[Tuple[str, str], int] = {}
        prev_kw = None
        prev_line = -1
        for kw, num_str, line_idx in seq:
            if num_str in ones:
                if prev_kw and prev_kw != kw:
                    if line_idx - prev_line <= 300:
                        pair = (prev_kw, kw)
                        votes[pair] = votes.get(pair, 0) + 1
            prev_kw = kw
            prev_line = line_idx

        # Resolve edges
        edges = set()
        for kw_a in found_kws:
            for kw_b in found_kws:
                if kw_a == kw_b:
                    continue
                v_ab = votes.get((kw_a, kw_b), 0)
                v_ba = votes.get((kw_b, kw_a), 0)
                if v_ab > v_ba:
                    edges.add((kw_a, kw_b))
                elif v_ab == v_ba and v_ab > 0:
                    # Tie-breaker: use pre-defined map
                    if keywords_map.get(kw_a, 99) < keywords_map.get(kw_b, 99):
                        edges.add((kw_a, kw_b))

        parents_of: dict[str, set[str]] = {k: set() for k in found_kws}
        children_of: dict[str, set[str]] = {k: set() for k in found_kws}
        for parent, child in edges:
            parents_of[child].add(parent)
            children_of[parent].add(child)

        roots = [k for k in found_kws if not parents_of[k]]
        levels: dict[str, int] = {}

        def assign_level(kw: str, depth: int, visited: set):
            if kw in visited:
                return # Prevent infinite loops in cycles
            if kw in levels and levels[kw] >= depth:
                return
            levels[kw] = depth
            for child in children_of.get(kw, set()):
                assign_level(child, depth + 1, visited | {kw})

        for r in roots:
            assign_level(r, 0, set())
            
        for kw in found_kws:
            if kw not in levels:
                assign_level(kw, 0, set())

        for kw in found_kws:
            if kw not in levels:
                levels[kw] = max(levels.values(), default=0) + 1

        # Resolve conflicts at the same level: if single-char and multi-char coexist,
        # keep only the single-char ones
        level_to_kws: Dict[int, List[str]] = {}
        for kw in found_kws:
            lvl = levels[kw]
            if lvl not in level_to_kws:
                level_to_kws[lvl] = []
            level_to_kws[lvl].append(kw)
            
        filtered_kws = []
        for lvl, kws in level_to_kws.items():
            single_chars = [k for k in kws if len(k) == 1]
            if single_chars:
                filtered_kws.extend(single_chars)
            else:
                filtered_kws.extend(kws)

        # Sort by derived level, then by first occurrence in sequences
        result = sorted(filtered_kws, key=lambda k: (levels[k], seq.index(next(x for x in seq if x[0] == k))))
        return ", ".join(result)

    def parse_chapters(self, file_path: str, regexes: List[str], encoding: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str]:
        actual_encoding: str = encoding if encoding else self.detect_encoding(file_path)
            
        chapters: List[Dict[str, Any]] = []
        patterns = [re.compile(p) for p in regexes if p]
        
        try:
            with open(file_path, 'r', encoding=actual_encoding, errors='replace') as f:
                lines = f.readlines()
                current_chapter: Optional[Dict[str, Any]] = None
                
                hierarchy: List[str] = [""] * len(patterns)
                
                for line_idx, line in enumerate(lines):
                    line_str = line.strip()
                    if not line_str or len(line_str) > 150:
                        continue
                        
                    matched_level: int = -1
                    for i, p in enumerate(patterns):
                        if p.match(line_str):
                            matched_level = i
                            break
                        
                    if matched_level >= 0:
                        # Close previous chapter
                        if current_chapter is not None:
                            current_chapter['line_end'] = line_idx - 1 # type: ignore
                            chapters.append(current_chapter)
                            current_chapter = None # Reset for next chapter
                        elif line_idx > 0:
                            # Prologue
                            prologue: Dict[str, Any] = {
                                'title': "前言_Prologue",
                                'raw_title': "前言_Prologue",
                                'hierarchy_path': [],
                                'line_start': 0,
                                'line_end': line_idx - 1
                            }
                            chapters.append(prologue)
                            
                        # Start new chapter
                        raw_title = line_str
                        raw_safe = re.sub(r'[\\/*?:"<>|]', "", raw_title) 
                        
                        hierarchy[matched_level] = raw_safe # type: ignore
                        for j in range(matched_level + 1, len(patterns)):
                            hierarchy[j] = "" # type: ignore
                            
                        title_prefix = ""
                        for j in range(matched_level):
                            if hierarchy[j]:
                                title_prefix += f"[{hierarchy[j]}] "
                                
                        full_title = f"{title_prefix}{raw_safe}".strip()
                        
                        current_chapter = {
                            'title': full_title,
                            'raw_title': raw_safe,
                            'hierarchy_path': [h for h in hierarchy[:matched_level+1] if h], # type: ignore
                            'line_start': line_idx,
                            'line_end': -1 
                        }
                
                # Close the final chapter
                if current_chapter is not None:
                    current_chapter['line_end'] = len(lines) - 1 # type: ignore
                    chapters.append(current_chapter)
                elif not chapters and lines:
                    # No chapters found, treat entire file as one part
                    chapters.append({
                        'title': "全文_FullText",
                        'raw_title': "全文_FullText",
                        'hierarchy_path': [],
                        'line_start': 0,
                        'line_end': len(lines) - 1
                    })
                    
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")
            
        return chapters, actual_encoding

    def _eval_cond(self, value: int, target: int, op: str) -> bool:
        """Evaluate a numeric comparison given an operator symbol."""
        if op in (">", "≈"):   return value > target
        if op == ">=":          return value >= target
        if op == "<":           return value < target
        if op == "<=":          return value <= target
        if op in ("==", "="):   return value == target
        return False  # unknown operator

    def split_file(self, file_path: str, chapters: List[Dict[str, Any]], output_dir: str, encoding: str = 'utf-8',
                   include_body: bool = True, skip_toc: bool = True,
                   max_length: int = 0, chunk_size: int = 0, chunk_break: str = "Sentence",
                   output_mode: str = "Flat Folder", constraint_limit: int = 0,
                   constraint_comparator: str = "≈", trigger_comparator: str = ">",
                   chunk_size_comparator: str = "≈", progress_callback=None):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if is_constraint_mode(output_mode):
            return self._split_by_constraint(file_path, output_dir, encoding, output_mode, constraint_limit,
                                              max_length, chunk_size, chunk_break,
                                              constraint_comparator, trigger_comparator, chunk_size_comparator,
                                              progress_callback)
            
        final_chapters = []
        
        # ── Read file lines once for TOC detection ──
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                all_lines: List[str] = f.readlines()
        except Exception:
            all_lines = []
        
        toc_header_re = re.compile(r'^[\s　]*(总目录|目\s*录|CONTENTS|TABLE\s+OF\s+CONTENTS)[\s　]*$', re.IGNORECASE)
        toc_footer_re = re.compile(r'(返回总目录|返回目录)', re.IGNORECASE)
        
        # ── Strategy A: Marker-bounded TOC regions ──
        # Scan file lines for TOC header → body → footer patterns
        marker_regions: List[Tuple[int, int]] = []
        i_line: int = 0
        while i_line < len(all_lines):
            text = all_lines[i_line].strip()
            if len(text) <= 30 and toc_header_re.match(text):
                region_start: int = i_line
                region_end: int = i_line
                for j in range(i_line + 1, min(i_line + 3000, len(all_lines))):  # type: ignore[operator]
                    j_text = all_lines[j].strip()
                    if toc_footer_re.search(j_text):
                        region_end = j
                        break
                    if len(j_text) > 200:
                        region_end = j - 1  # type: ignore[operator]
                        break
                    region_end = j
                if region_end > region_start + 3:  # type: ignore[operator]
                    marker_regions.append((region_start, region_end))
                i_line = region_end + 1
            else:
                i_line += 1
        
        # ── Strategy B: Dense heading clusters (fallback) ──
        raw_clusters: List[Tuple[int, int]] = []
        if len(chapters) > 2:
            cluster_start: Optional[int] = None
            dense_count: int = 0
            for ci in range(len(chapters) - 1):
                gap: int = chapters[ci + 1]['line_start'] - chapters[ci]['line_start']
                if gap <= 2:
                    if cluster_start is None:
                        cluster_start = ci
                        dense_count = 2
                    else:
                        dense_count += 1
                else:
                    if cluster_start is not None and dense_count >= 8:
                        raw_clusters.append((cluster_start, ci))
                    cluster_start = None
                    dense_count = 0
            if cluster_start is not None and dense_count >= 8:
                raw_clusters.append((cluster_start, len(chapters) - 1))
        
        # ── Build toc_indices from both strategies ──
        toc_indices = set()
        
        # From marker regions: any chapter whose line_start falls within a marker region
        for r_start, r_end in marker_regions:
            for ci, ch in enumerate(chapters):
                if r_start <= ch['line_start'] <= r_end:
                    toc_indices.add(ci)
        
        # From dense clusters (only those not already covered by marker regions)
        for cs, ce in raw_clusters:
            cluster_line = chapters[cs]['line_start']
            already_marked = any(r_start <= cluster_line <= r_end for r_start, r_end in marker_regions)
            if not already_marked:
                for ci in range(cs, ce + 1):
                    toc_indices.add(ci)
        
        # Compute toc_regions for the merge-TOC-files logic
        # Group contiguous toc_indices into regions
        toc_regions = []   # list of (chapter_start_idx, chapter_end_idx)
        if toc_indices:
            sorted_idx: List[int] = sorted(toc_indices)
            rg_start = sorted_idx[0]
            rg_end = sorted_idx[0]
            for ci in cast(List[int], sorted_idx[1:]):
                if ci == rg_end + 1:
                    rg_end = ci
                else:
                    toc_regions.append((rg_start, rg_end))
                    rg_start = ci
                    rg_end = ci
            toc_regions.append((rg_start, rg_end))
        
        
        if skip_toc:
            # Simply remove all chapters in TOC regions
            for i, ch in enumerate(chapters):
                if i not in toc_indices:
                    final_chapters.append(ch)
        else:
            # Keep body chapters, merge each TOC region into a single "目录" file
            toc_region_idx: int = 0
            i: int = 0
            while i < len(chapters):
                if i in toc_indices:
                    for rs, re_ in toc_regions:
                        if rs <= i <= re_:
                            region_start_line = max(0, chapters[rs]['line_start'] - 5)  # include TOC header
                            region_end_line = chapters[re_].get('line_end', chapters[re_]['line_start'])
                            toc_region_idx += 1  # type: ignore[operator]
                            if toc_region_idx == 1 and len(toc_regions) > 1:
                                toc_label = "总目录"
                            else:
                                toc_label = f"目录_{toc_region_idx}"
                            final_chapters.append({
                                'title': toc_label,
                                'raw_title': toc_label,
                                'hierarchy_path': [],
                                'line_start': region_start_line,
                                'line_end': region_end_line
                            })
                            i = re_ + 1
                            break
                    else:
                        i += 1
                else:
                    final_chapters.append(chapters[i])
                    i += 1

        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                lines = f.readlines()
                
                valid_chapters = []
                for chapter in final_chapters:
                    start = int(chapter.get('line_start', 0))
                    end = int(chapter.get('line_end', len(lines))) + 1
                    content = lines[start:end] # type: ignore
                    
                    # Filter out chapters with no real content
                    non_empty_count = sum(1 for c_line in content if c_line.strip())
                    
                    if include_body and non_empty_count <= 2 and chapter['title'] not in ['前言_Prologue', '全文_FullText']:
                        continue
                        
                    if not include_body:
                        content = [lines[start]] # type: ignore
                        
                    content_str = "".join(content)
                    char_count = len(content_str)
                    
                    if max_length > 0 and chunk_size > 0 and include_body:
                        # Dynamic comparator evaluation using trigger_comparator
                        if self._eval_cond(char_count, max_length, trigger_comparator):
                            # Split this large chapter into chunks
                            chunks = self._chunk_content(content_str, chunk_size, chunk_break) # type: ignore
                            for i, chunk_text in enumerate(chunks):
                                sub_chapter = chapter.copy()
                                sub_chapter['title'] = f"{chapter['title']} (第{i+1}部分)"
                                sub_chapter['raw_title'] = f"{chapter.get('raw_title', chapter['title'])} (第{i+1}部分)"
                                valid_chapters.append((sub_chapter, [chunk_text]))
                        else:
                            valid_chapters.append((chapter, content))
                    else:
                        valid_chapters.append((chapter, content))
                    
                total_chapters = len(valid_chapters)
                
                for idx, (chapter, content) in enumerate(valid_chapters):
                    safe_title = chapter['title'].strip()
                    
                    if "Nested" in output_mode:
                        target_dir = output_dir
                        
                        h_path = chapter.get('hierarchy_path', [])
                        if len(h_path) > 1:
                            # Determine how many folder levels to use
                            if "Nested:1" in output_mode:
                                folder_levels = h_path[:1]        # volume only
                            elif "Nested:2" in output_mode:
                                folder_levels = h_path[:2]        # volume + chapter
                            else:
                                folder_levels = h_path[:-1]        # all levels (original behaviour)
                            
                            for folder in folder_levels:
                                folder_safe = re.sub(r'[\\/*?:"<>|]', "", folder.strip())
                                if folder_safe:
                                    target_dir = os.path.join(target_dir, folder_safe) # type: ignore
                        
                        os.makedirs(target_dir, exist_ok=True)
                        
                        raw_safe = chapter.get('raw_title', safe_title).strip()
                        filename = f"{idx+1:03d}_{raw_safe}.txt"
                        out_path = os.path.join(target_dir, filename) # type: ignore
                    else:
                        # Flat Folder
                        filename = f"{idx+1:03d}_{safe_title}.txt"
                        out_path = os.path.join(output_dir, filename)
                    
                    with open(out_path, 'w', encoding='utf-8') as out_f:
                        out_f.writelines(content)
                        
                    if progress_callback:
                        progress_callback(idx + 1, total_chapters)
                        
        except Exception as e:
            raise Exception(f"Error splitting file: {str(e)}")
            
    def preview_constraint(self, file_path: str, encoding: str, mode: str, limit: int,
                            max_length: int, chunk_size: int, chunk_break: str,
                            constraint_comparator: str = "≈", trigger_comparator: str = ">",
                            chunk_size_comparator: str = "≈"):
        """
        Simulates constraint splitting without writing files. Returns a preview representation.
        """
        if limit <= 0:
            raise ValueError("Constraint limit must be greater than 0.")
            
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()

            chunks = self._build_constraint_chunks(
                content=content,
                mode=mode,
                limit=limit,
                max_length=max_length,
                chunk_size=chunk_size,
                chunk_break=chunk_break,
                trigger_comparator=trigger_comparator,
                paragraph_joiner="\n",
            )
                
            # Create simulated chapters for preview
            simulated_chapters = []
            current_line = 0
            for i, chunk_str in enumerate(chunks):
                lines_in_chunk = chunk_str.count('\n') + 1
                simulated_chapters.append({
                    'title': f"[预览] 第 {i+1} 部分",
                    'line_start': current_line,
                    'line_end': current_line + lines_in_chunk - 1,
                    'size_chars': len(chunk_str)
                })
                current_line += lines_in_chunk
                
            return simulated_chapters
            
        except Exception as e:
            raise Exception(f"Constraint Preview failed: {str(e)}")

    def _split_by_constraint(self, file_path: str, output_dir: str, encoding: str, mode: str, limit: int,
                              max_length: int, chunk_size: int, chunk_break: str,
                              constraint_comparator: str = "≈", trigger_comparator: str = ">",
                              chunk_size_comparator: str = "≈", progress_callback=None):
        if limit <= 0:
            raise ValueError("Constraint limit must be greater than 0.")
            
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()

            chunks = self._build_constraint_chunks(
                content=content,
                mode=mode,
                limit=limit,
                max_length=max_length,
                chunk_size=chunk_size,
                chunk_break=chunk_break,
                trigger_comparator=trigger_comparator,
                paragraph_joiner="\n\n",
            )
                
            total_chunks = len(chunks)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            # Drop loader cache hash suffix so output names follow the source file name.
            base_name = re.sub(r"_[0-9a-f]{12}$", "", base_name)
            
            for idx, chunk_str in enumerate(chunks):
                out_path = os.path.join(output_dir, f"{base_name}_Part{idx+1:03d}.txt")
                with open(out_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(chunk_str)
                    
                if progress_callback:
                    progress_callback(idx + 1, total_chunks)
                    
        except Exception as e:
            raise Exception(f"Constraint Splitting failed: {str(e)}")
            
        return True

    def _build_constraint_chunks(
        self,
        content: str,
        mode: str,
        limit: int,
        max_length: int,
        chunk_size: int,
        chunk_break: str,
        trigger_comparator: str,
        paragraph_joiner: str,
    ) -> List[str]:
        chunks: List[str] = []

        if is_size_mode(mode):
            # Approximate split by bytes, assuming ~3 bytes per Chinese character.
            char_limit = (limit * 1024) // 3
            chunks = self._chunk_content(content, char_limit, "Exact Size")
        elif is_word_mode(mode):
            chunks = self._chunk_content(content, limit, chunk_break)
        elif is_line_mode(mode):
            lines = content.splitlines(keepends=True)
            chunks = ["".join(lines[i:i + limit]) for i in range(0, len(lines), limit)]  # type: ignore
        elif is_paragraph_mode(mode):
            paragraphs = [p for p in re.split(r'\n+', content) if p.strip()]
            for i in range(0, len(paragraphs), limit):
                chunks.append(paragraph_joiner.join(paragraphs[i:i + limit]) + paragraph_joiner)  # type: ignore
        else:
            chunks = [content]

        if max_length > 0 and chunk_size > 0 and needs_secondary_constraint_chunking(mode):
            refined_chunks: List[str] = []
            for chunk_str in chunks:
                if self._eval_cond(len(chunk_str), max_length, trigger_comparator):
                    refined_chunks.extend(self._chunk_content(chunk_str, chunk_size, chunk_break))
                else:
                    refined_chunks.append(chunk_str)
            return refined_chunks

        return chunks

    def _chunk_content(self, text: str, chunk_size: int, break_mode: str) -> List[str]:
        """
        Splits a very long text into chunks of at least `chunk_size` characters.
        break_mode: 'Paragraph', 'Sentence', or 'Exact Size'
        """
        chunks: List[str] = []
        current_idx: int = 0
        total_len: int = len(text)
        
        break_pattern: Any = None
        if "Paragraph" in break_mode:
            break_pattern = re.compile(r'\n+')
        elif "Sentence" in break_mode:
            break_pattern = re.compile(r'(\n+|[。！？.!?]\s*)')
        else: # Exact Size / None
            break_pattern = None
        
        while current_idx < total_len:
            # If remaining text is smaller than chunk size plus buffer
            remaining: int = total_len - current_idx # type: ignore
            remain_limit: int = int(chunk_size * 1.5)
            
            if remaining <= remain_limit and break_pattern is not None:
                chunks.append(str(text[current_idx:])) # type: ignore
                break
            elif remaining <= chunk_size and break_pattern is None:
                chunks.append(str(text[current_idx:])) # type: ignore
                break
                
            # Move forward by chunk_size
            target_idx: int = current_idx + chunk_size # type: ignore
            
            if break_pattern: # type: ignore
                # Find the next good break point AFTER target_idx
                match = break_pattern.search(text, target_idx)
                if match:
                    break_idx = match.end()
                    chunks.append(str(text[current_idx:break_idx])) # type: ignore
                    current_idx = break_idx
                else:
                    chunks.append(str(text[current_idx:total_len])) # type: ignore
                    break
            else:
                chunks.append(str(text[current_idx:target_idx])) # type: ignore
                current_idx = target_idx
                
        return chunks

    def detect_multilang_from_toc(self, file_path: str, encoding: str) -> List[str]:
        """
        Analyze the Table of Contents (TOC) to identify multiple languages.
        Heuristic frequency-based detection (bbbz123 optimized).
        Applies both 'zh' and 'en' heading regexes to see if both yield significant chapter hits.
        Returns ['zh', 'en'] if both are detected, otherwise an empty list.
        """
        # If encoding is not provided, detect it (bbbz123: ensure robust encoding handling)
        if not encoding:
            encoding = self.detect_encoding(file_path)
            
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                lines: List[str] = f.readlines()
        except Exception:
            return []
            
        zh_config = get_language('zh')
        en_config = get_language('en')
        
        toc_start = -1
        # Use Chinese TOC regex roughly since it's most common for dual-lang books here
        # Actually check both toc headers (bbbz123: improved TOC header detection)
        for i, line in enumerate(lines[:500]):
            text_strip = line.strip()
            if zh_config.toc_header_regex.search(text_strip) or en_config.toc_header_regex.search(text_strip):
                toc_start = i + 1
                break
                
        if toc_start < 0:
            return []
            
        zh_count = 0
        en_count = 0
        blank_streak = 0
        
        for idx, line in enumerate(lines[toc_start:toc_start + 5000]):
            text = line.strip()
            if not text:
                blank_streak += 1
                if blank_streak > 5:
                    break
                continue
            blank_streak = 0
            if len(text) > 120:
                continue
                
            if zh_config.heading_regex.search(text):
                zh_count += 1
            if en_config.heading_regex.search(text):
                en_count += 1
                
        if zh_count >= 3 and en_count >= 3:
            return ['zh', 'en']
        return []
    def resolve_languages(self, file_path: str, encoding: str, user_lang_id: Optional[str] = None) -> List[str]:
        """
        Logic to determine which languages should be scanned for this file.
        Consolidated from gui/app.py for bbbz123.
        """
        from core.patterns import detect_all_languages
        
        try:
            if not user_lang_id or "auto" in user_lang_id.lower():
                filename_lower = os.path.basename(file_path).lower()
                bilingual_keywords = ['双语', '中英', '英汉', '汉英', 'bilingual']
                if any(kw in filename_lower for kw in bilingual_keywords):
                    return ['zh', 'en']
                
                lang_ids = self.detect_multilang_from_toc(file_path, encoding)
                if not lang_ids:
                    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                        sample = f.read(50000)
                    return detect_all_languages(sample)
                return lang_ids
                
            if user_lang_id == 'multi':
                lang_ids = self.detect_multilang_from_toc(file_path, encoding)
                if not lang_ids:
                    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                        sample = f.read(200000)
                    lang_ids = detect_all_languages(sample)
                    if len(lang_ids) < 2:
                        return ['zh', 'en']
                return lang_ids
            
            return [user_lang_id]
        except Exception:
            return ['zh', 'en'] if user_lang_id == 'multi' else ['zh']
