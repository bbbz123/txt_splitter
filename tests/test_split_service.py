import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.parser import TextParser
from core.split_service import SplitService


def _default_global_settings(output_dir: str, mode: str) -> dict:
    return {
        "mode": mode,
        "strategy": "Flat 同级输出",
        "structure": "章",
        "language": "zh",
        "constraint_limit": "5",
        "constraint_comparator": "≈ 约等于",
        "chunk_break": "Sentence 就近句号",
        "max_length": "1500",
        "chunk_size": "500",
        "enable_chunking": False,
        "trigger_comparator": "≈ 约等于",
        "chunk_size_comparator": "≈ 约等于",
        "include_body": True,
        "skip_toc": True,
        "output_dir": output_dir,
    }


def test_split_service_scan_returns_results(tmp_path):
    parser = TextParser()
    service = SplitService(parser)
    test_file = os.path.join(project_root, "tests", "dummy_novel.txt")

    scan = service.scan_files(
        selected_files=[test_file],
        global_settings=_default_global_settings(str(tmp_path), "📜 智能章节模式"),
        file_settings={},
    )

    assert scan.failed_files == []
    assert test_file in scan.parsed_chapters
    lang_blocks = scan.parsed_chapters[test_file]
    assert isinstance(lang_blocks, dict)
    assert len(lang_blocks) >= 1


def test_split_service_constraint_split_writes_files(tmp_path):
    parser = TextParser()
    service = SplitService(parser)
    test_file = os.path.join(project_root, "tests", "dummy_novel.txt")

    result = service.split_files(
        selected_files=[test_file],
        global_settings=_default_global_settings(str(tmp_path), "📄 按行数切分"),
        file_settings={},
        parsed_chapters={},
    )

    assert result.failed_files == []
    out_files = [p for p in os.listdir(tmp_path) if p.endswith(".txt")]
    assert len(out_files) >= 2
