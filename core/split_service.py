"""Application service layer for scanning and splitting.

This module contains UI-agnostic orchestration logic so GUI code can focus on
rendering and user interaction only.
"""

from __future__ import annotations

import datetime
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from core.mode_utils import (
    is_chapter_mode,
    is_constraint_mode,
    is_word_mode,
)
from core.parser import TextParser
from core.patterns import build_regexes_from_tokens, get_all_languages, get_language


StatusCallback = Callable[[str], None]
FileStartCallback = Callable[[int, int, str], None]
BatchProgressCallback = Callable[[int, int], None]
ChunkProgressCallback = Callable[[int, int], None]


@dataclass
class ScanResult:
    parsed_chapters: Dict[str, Dict[str, List[Dict[str, Any]]]] = field(default_factory=dict)
    first_encoding: Optional[str] = None
    failed_files: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class SplitResult:
    failed_files: List[Tuple[str, str]] = field(default_factory=list)
    total_files: int = 0
    output_dir: str = ""


class SplitService:
    def __init__(self, parser: TextParser):
        self.parser = parser

    def scan_files(
        self,
        selected_files: Sequence[str],
        global_settings: Dict[str, Any],
        file_settings: Dict[str, Dict[str, Any]],
        preview_limit: int = 10,
        status_callback: Optional[StatusCallback] = None,
    ) -> ScanResult:
        result = ScanResult()
        preview_files = list(selected_files)[:preview_limit]
        is_batch = len(selected_files) > 1

        for idx, file_path in enumerate(preview_files):
            if status_callback:
                status_callback(f"预览分析中 ({idx + 1}/{len(preview_files)}): {os.path.basename(file_path)}")

            f_settings = file_settings.get(file_path, {})

            def get_s(key: str):
                return self._resolve_setting(f_settings, global_settings, key)

            file_results: Dict[str, List[Dict[str, Any]]] = {}

            try:
                with self.parser.prepared_document(file_path) as prepared:
                    working_file_path = prepared.working_text_path
                    encoding = prepared.encoding
                    if idx == 0:
                        result.first_encoding = encoding

                    mode = str(get_s("mode"))
                    if is_constraint_mode(mode):
                        limit = self._safe_int(get_s("constraint_limit"), 500)
                        max_length = 0
                        chunk_size = 0
                        if bool(global_settings.get("enable_chunking")) and not is_word_mode(mode):
                            max_length = self._safe_int(global_settings.get("max_length"), 0)
                            chunk_size = self._safe_int(global_settings.get("chunk_size"), 0)

                        chunk_break = str(get_s("chunk_break")).split()[0]
                        chapters = self.parser.preview_constraint(
                            file_path=working_file_path,
                            encoding=encoding,
                            mode=mode,
                            limit=limit,
                            max_length=max_length,
                            chunk_size=chunk_size,
                            chunk_break=chunk_break,
                            constraint_comparator=self._map_ui_comparator(str(get_s("constraint_comparator"))),
                            trigger_comparator=self._map_ui_comparator(str(global_settings.get("trigger_comparator", "≈"))),
                            chunk_size_comparator=self._map_ui_comparator(str(global_settings.get("chunk_size_comparator", "≈"))),
                        )
                        if chapters:
                            for c in chapters:
                                c["is_constraint"] = True
                            file_results["zh"] = chapters
                    else:
                        lang_id = self._resolve_language_id(
                            per_file_lang=f_settings.get("language"),
                            global_lang=global_settings.get("language"),
                        )
                        lang_ids = self.parser.resolve_languages(working_file_path, encoding, lang_id)

                        if prepared.has_native_structure and prepared.native_chapters:
                            primary_lang = lang_ids[0] if lang_ids else "zh"
                            file_results[primary_lang] = prepared.native_chapters
                        else:
                            structure = str(get_s("structure")).replace("，", ",")
                            if is_batch and f_settings.get("structure", "") == "":
                                primary_lang = lang_ids[0] if lang_ids else "zh"
                                structure = self.parser.analyze_structure(
                                    working_file_path,
                                    encoding=encoding,
                                    lang=primary_lang,
                                ).replace("，", ",")

                            tokens = [t.strip() for t in structure.split(",") if t.strip()]
                            if not tokens:
                                tokens = ["章"]

                            for lid in lang_ids:
                                regexes = build_regexes_from_tokens(tokens, lid)
                                if not regexes:
                                    continue
                                chapters, _ = self.parser.parse_chapters(working_file_path, regexes, encoding)
                                if chapters:
                                    file_results[lid] = chapters

                if file_results:
                    result.parsed_chapters[file_path] = file_results
            except Exception as file_exc:  # noqa: BLE001
                result.failed_files.append((os.path.basename(file_path), str(file_exc)))

        return result

    def split_files(
        self,
        selected_files: Sequence[str],
        global_settings: Dict[str, Any],
        file_settings: Dict[str, Dict[str, Any]],
        parsed_chapters: Dict[str, Dict[str, List[Dict[str, Any]]]],
        file_start_callback: Optional[FileStartCallback] = None,
        batch_progress_callback: Optional[BatchProgressCallback] = None,
        chunk_progress_callback: Optional[ChunkProgressCallback] = None,
    ) -> SplitResult:
        total_files = len(selected_files)
        base_out_path = str(global_settings.get("output_dir", ""))
        output_dir = base_out_path

        if total_files > 1:
            batch_folder_name = f"批量输出_Batch_{datetime.datetime.now().strftime('%H%M%S')}"
            output_dir = os.path.join(base_out_path, batch_folder_name)
            os.makedirs(output_dir, exist_ok=True)

        failed_files: List[Tuple[str, str]] = []

        for file_idx, file_path in enumerate(selected_files):
            file_base_name = os.path.basename(file_path)
            if file_start_callback:
                file_start_callback(file_idx + 1, total_files, file_base_name)

            file_out_dir = output_dir
            if total_files > 1:
                file_out_dir = os.path.join(output_dir, os.path.splitext(file_base_name)[0])
                os.makedirs(file_out_dir, exist_ok=True)

            f_settings = file_settings.get(file_path, {})

            def get_s(key: str):
                return self._resolve_setting(f_settings, global_settings, key)

            try:
                with self.parser.prepared_document(file_path) as prepared:
                    working_file_path = prepared.working_text_path
                    encoding = prepared.encoding
                    mode = str(get_s("mode"))

                    if is_chapter_mode(mode):
                        strat = str(get_s("strategy"))
                        if "Nested" in strat:
                            m = re.search(r"Nested/(\d+)", strat)
                            mode = f"Nested:{m.group(1)}" if m else "Nested"
                        else:
                            mode = "Flat"

                    is_constraint = is_constraint_mode(mode)
                    curr_kwargs: Dict[str, Any] = {
                        "output_dir": file_out_dir,
                        "include_body": bool(global_settings.get("include_body", True)),
                        "skip_toc": bool(global_settings.get("skip_toc", True)),
                        "output_mode": mode,
                    }

                    if is_constraint:
                        limit = self._safe_int(get_s("constraint_limit"), 500)
                        max_length = 0
                        chunk_size = 0
                        if bool(global_settings.get("enable_chunking")) and not is_word_mode(mode):
                            max_length = self._safe_int(global_settings.get("max_length"), 0)
                            chunk_size = self._safe_int(global_settings.get("chunk_size"), 0)

                        chunk_break = str(get_s("chunk_break")).split()[0]
                        curr_kwargs.update(
                            {
                                "constraint_limit": limit,
                                "max_length": max_length,
                                "chunk_size": chunk_size,
                                "chunk_break": chunk_break,
                                "constraint_comparator": self._map_ui_comparator(str(get_s("constraint_comparator"))),
                                "trigger_comparator": self._map_ui_comparator(str(global_settings.get("trigger_comparator", "≈"))),
                                "chunk_size_comparator": self._map_ui_comparator(str(global_settings.get("chunk_size_comparator", "≈"))),
                            }
                        )

                        chapters = self.parser.preview_constraint(
                            working_file_path,
                            encoding,
                            mode,
                            limit,
                            max_length,
                            chunk_size,
                            chunk_break,
                            curr_kwargs["constraint_comparator"],
                            curr_kwargs["trigger_comparator"],
                            curr_kwargs["chunk_size_comparator"],
                        )
                        self.parser.split_file(
                            file_path=working_file_path,
                            chapters=chapters,
                            encoding=encoding,
                            progress_callback=chunk_progress_callback if total_files == 1 else None,
                            **curr_kwargs,
                        )
                    else:
                        if file_path in parsed_chapters:
                            lang_results = parsed_chapters[file_path]
                        elif prepared.has_native_structure and prepared.native_chapters:
                            primary_lang = global_settings.get("language") or "zh"
                            if primary_lang == "multi":
                                primary_lang = "zh"
                            lang_results = {str(primary_lang): prepared.native_chapters}
                        else:
                            lang_results: Dict[str, List[Dict[str, Any]]] = {}
                            lang_id = self._resolve_language_id(
                                per_file_lang=f_settings.get("language"),
                                global_lang=global_settings.get("language"),
                            )
                            lang_ids = self.parser.resolve_languages(working_file_path, encoding, lang_id)

                            structure_raw = str(get_s("structure")).replace("，", ",")
                            if total_files > 1 and f_settings.get("structure", "") == "":
                                primary_lang = lang_ids[0] if lang_ids else "zh"
                                structure_raw = self.parser.analyze_structure(
                                    working_file_path,
                                    encoding=encoding,
                                    lang=primary_lang,
                                ).replace("，", ",")

                            tokens = [t.strip() for t in structure_raw.split(",") if t.strip()]
                            if not tokens:
                                tokens = ["章"]

                            for lid in lang_ids:
                                regexes = build_regexes_from_tokens(tokens, lid)
                                if not regexes:
                                    continue
                                chaps, _ = self.parser.parse_chapters(working_file_path, regexes, encoding)
                                if chaps:
                                    lang_results[lid] = chaps

                        if len(lang_results) <= 1:
                            cid = next(iter(lang_results), "zh")
                            chapters = lang_results.get(cid, [])
                            self.parser.split_file(
                                file_path=working_file_path,
                                chapters=chapters,
                                encoding=encoding,
                                progress_callback=chunk_progress_callback if total_files == 1 else None,
                                **curr_kwargs,
                            )
                        else:
                            if total_files == 1:
                                nested_dir = os.path.join(output_dir, os.path.splitext(file_base_name)[0])
                                os.makedirs(nested_dir, exist_ok=True)
                                file_out_dir = nested_dir

                            for lid, chapters in lang_results.items():
                                lang_name = get_language(lid).display_name
                                lang_out_dir = os.path.join(file_out_dir, lang_name)
                                os.makedirs(lang_out_dir, exist_ok=True)

                                lang_kwargs = curr_kwargs.copy()
                                lang_kwargs["output_dir"] = lang_out_dir
                                self.parser.split_file(
                                    file_path=working_file_path,
                                    chapters=chapters,
                                    encoding=encoding,
                                    **lang_kwargs,
                                )
            except Exception as file_exc:  # noqa: BLE001
                failed_files.append((file_base_name, str(file_exc)))

            if total_files > 1 and batch_progress_callback:
                batch_progress_callback(file_idx + 1, total_files)

        return SplitResult(
            failed_files=failed_files,
            total_files=total_files,
            output_dir=output_dir if total_files > 1 else base_out_path,
        )

    @staticmethod
    def _resolve_setting(
        f_settings: Dict[str, Any],
        global_settings: Dict[str, Any],
        key: str,
    ):
        val = f_settings.get(key)
        if val is not None and val != "" and val not in {"跟随全局 (Global)", "跟随全局"}:
            return val
        return global_settings[key]

    @staticmethod
    def _safe_int(value: Any, default: int) -> int:
        try:
            return int(value)
        except Exception:  # noqa: BLE001
            return default

    @staticmethod
    def _map_ui_comparator(label: str) -> str:
        mapping = {
            "≈ 约等于": "≈",
            "= 等于": "==",
            "> 大于": ">",
            "≥ 大于等于": ">=",
            "< 小于": "<",
            "≤ 小于等于": "<=",
        }
        return mapping.get(label, label)

    @staticmethod
    def _resolve_language_id(per_file_lang: Any, global_lang: Any) -> Optional[str]:
        lang_value = per_file_lang
        if lang_value in (None, "", "跟随全局", "跟随全局 (Global)"):
            lang_value = global_lang

        if lang_value in (None, ""):
            return None

        if isinstance(lang_value, str):
            lv = lang_value
            lower = lv.lower()
            if "auto" in lower:
                return None
            if "multi" in lower:
                return "multi"

            for lp in get_all_languages():
                if lv == lp.lang_id:
                    return lp.lang_id
                if lp.display_name in lv:
                    return lp.lang_id

        return str(lang_value)
