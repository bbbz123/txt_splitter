import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.mode_utils import (  # noqa: E402
    is_chapter_mode,
    is_constraint_mode,
    is_line_mode,
    is_paragraph_mode,
    is_size_mode,
    is_word_mode,
    needs_secondary_constraint_chunking,
)


def test_constraint_mode_detection():
    assert is_constraint_mode("📑 按段落切分")
    assert is_constraint_mode("By Word Count")
    assert is_constraint_mode("By Line Count")
    assert is_constraint_mode("By File Size (KB)")
    assert not is_constraint_mode("📜 智能章节模式")


def test_sub_mode_detection():
    assert is_size_mode("🗂️ 按文件大小 (KB)")
    assert is_word_mode("📝 按字数切分")
    assert is_line_mode("📄 按行数切分")
    assert is_paragraph_mode("📑 按段落切分")
    assert is_paragraph_mode("By Paragraph Count")

    assert needs_secondary_constraint_chunking("📄 按行数切分")
    assert needs_secondary_constraint_chunking("📑 按段落切分")
    assert not needs_secondary_constraint_chunking("📝 按字数切分")


def test_chapter_mode_detection():
    assert is_chapter_mode("📜 智能章节模式")
    assert is_chapter_mode("Regex Mode")
    assert is_chapter_mode("Chapter Mode")
    assert not is_chapter_mode("📄 按行数切分")
