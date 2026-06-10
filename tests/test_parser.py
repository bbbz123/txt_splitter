import os
import sys
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.parser import TextParser
from core.patterns import get_language, build_regexes_from_tokens

def test_parser():
    parser = TextParser()
    test_file = os.path.join(project_root, 'tests', 'dummy_novel.txt')
    out_dir = os.path.join(project_root, 'tests', 'output_test')
    
    print(f"Testing with file: {test_file}")
    
    # 1. Test encoding detection
    enc = parser.detect_encoding(test_file)
    print(f"Detected Encoding: {enc}")
    
    # 2. Test chapter parsing (Chinese)
    pattern = get_language('zh').preset_patterns["Common All (卷/编/篇/章/回/节)"] # Default pattern
    chapters, final_enc = parser.parse_chapters(test_file, [pattern], enc)
    
    print(f"Found {len(chapters)} chapters:")
    for c in chapters:
        print(f" - {c['title']} (Lines: {c['line_start']}-{c['line_end']})")
        
    assert len(chapters) == 6, f"Expected 6 chapters, got {len(chapters)}"
    
    # 3. Test splitting
    print(f"\nSplitting to {out_dir}...")
    def prog(curr, tot):
        print(f"Progress: {curr}/{tot}")
        
    parser.split_file(test_file, chapters, out_dir, final_enc, progress_callback=prog)
    print("Split complete!")


def test_english_parser():
    """Test English novel chapter parsing."""
    parser = TextParser()
    test_file = os.path.join(project_root, 'tests', 'dummy_english.txt')
    
    print(f"\n{'='*30}")
    print(f"Testing English with file: {test_file}")
    
    enc = parser.detect_encoding(test_file)
    print(f"Detected Encoding: {enc}")
    
    # Test with English "All Levels" pattern
    en_patterns = get_language('en').preset_patterns
    pattern = en_patterns["All Levels (Book/Part/Chapter)"]
    chapters, final_enc = parser.parse_chapters(test_file, [pattern], enc)
    
    print(f"Found {len(chapters)} chapters (All Levels):")
    for c in chapters:
        print(f" - {c['title']} (Lines: {c['line_start']}-{c['line_end']})")
    
    # We expect: Prologue + Part One + Chapter 1 + Chapter 2 + Part Two + Chapter Three = 6
    # But Prologue and Epilogue are fixed titles, not matched by "All Levels"
    # So we expect: Prologue (auto) + Part One + Chapter 1 + Chapter 2 + Part Two + Chapter Three = 6
    assert len(chapters) >= 5, f"Expected at least 5 English chapters, got {len(chapters)}"
    
    # Test with Chapter Only pattern
    pattern_ch = en_patterns["Chapter Only"]
    chapters_ch, _ = parser.parse_chapters(test_file, [pattern_ch], enc)
    print(f"\nFound {len(chapters_ch)} chapters (Chapter Only):")
    for c in chapters_ch:
        print(f" - {c['title']}")
    
    assert len(chapters_ch) >= 3, f"Expected at least 3 chapter-only entries, got {len(chapters_ch)}"
    
    # Test build_regexes_from_tokens 
    regexes = build_regexes_from_tokens(["Chapter", "Part"], 'en')
    assert len(regexes) == 2, f"Expected 2 regexes, got {len(regexes)}"
    print(f"\nBuilt regexes from tokens: {regexes}")
    
    # Test analyze_structure for English
    struct = parser.analyze_structure(test_file, encoding=enc, lang='en')
    print(f"\nDetected English structure: {struct}")
    
    print("\nEnglish tests passed!")


def test_late_dense_heading_cluster_is_not_treated_as_toc(tmp_path: Path):
    parser = TextParser()
    source = tmp_path / "late_dense_headings.txt"
    output_dir = tmp_path / "out"

    lines = ["第一章 正文开始\n"]
    lines.extend(f"正文段落 {i}\n" for i in range(35))
    lines.extend(f"第{i}章 短条目\n" for i in range(2, 12))
    source.write_text("".join(lines), encoding="utf-8")

    pattern = get_language("zh").preset_patterns["Common All (卷/编/篇/章/回/节)"]
    chapters, encoding = parser.parse_chapters(str(source), [pattern], "utf-8")

    parser.split_file(
        str(source),
        chapters,
        str(output_dir),
        encoding,
        output_mode="Flat Folder",
        skip_toc=True,
        include_body=False,
    )

    out_files = sorted(path.name for path in output_dir.glob("*.txt"))
    assert len(out_files) == 11
    assert any("第2章 短条目" in name for name in out_files)
    assert any("第11章 短条目" in name for name in out_files)


if __name__ == "__main__":
    test_parser()
    test_english_parser()

