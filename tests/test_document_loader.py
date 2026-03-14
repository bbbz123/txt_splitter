import os
import sys

import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.document_loader import DocumentLoader, SUPPORTED_INPUT_EXTS  # noqa: E402


def test_supported_extensions_include_all_targets():
    expected = {".txt", ".md", ".pdf", ".epub", ".docx", ".mobi", ".azw3"}
    assert expected.issubset(SUPPORTED_INPUT_EXTS)


def test_prepare_txt_uses_original_path():
    loader = DocumentLoader()
    txt_path = os.path.join(project_root, "tests", "dummy_novel.txt")

    doc = loader.prepare(txt_path)
    try:
        assert doc.source_ext == ".txt"
        assert doc.working_text_path == txt_path
        assert doc.encoding
        assert doc.native_chapters is None
        assert doc.has_native_structure is False
    finally:
        loader.cleanup(doc)


def test_prepare_markdown_extracts_headings(tmp_path):
    loader = DocumentLoader()
    sample = tmp_path / "sample.md"
    sample.write_text(
        "# Book Title\n\nIntro paragraph.\n\n## Chapter One\nBody A.\n\n## Chapter Two\nBody B.\n",
        encoding="utf-8",
    )

    doc = loader.prepare(str(sample))
    try:
        assert doc.source_ext == ".md"
        assert doc.working_text_path != str(sample)
        assert doc.encoding == "utf-8"
        assert doc.has_native_structure is True
        assert doc.native_chapters is not None
        assert [chapter["raw_title"] for chapter in doc.native_chapters] == [
            "Book Title",
            "Chapter One",
            "Chapter Two",
        ]
        assert doc.native_chapters[1]["hierarchy_path"] == ["Book Title", "Chapter One"]
    finally:
        loader.cleanup(doc)


def test_prepare_markdown_ignores_front_matter_and_code_fences(tmp_path):
    loader = DocumentLoader()
    sample = tmp_path / "sample.md"
    sample.write_text(
        "---\n"
        "title: Demo\n"
        "---\n\n"
        "# Book Title\n\n"
        "```md\n"
        "## Not A Real Chapter\n"
        "```\n\n"
        "## Chapter One\n"
        "Body.\n",
        encoding="utf-8",
    )

    doc = loader.prepare(str(sample))
    try:
        assert doc.native_chapters is not None
        assert [chapter["raw_title"] for chapter in doc.native_chapters] == [
            "Book Title",
            "Chapter One",
        ]
    finally:
        loader.cleanup(doc)


def test_prepare_unsupported_extension_raises(tmp_path):
    loader = DocumentLoader()
    sample = tmp_path / "sample.rst"
    sample.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError):
        loader.prepare(str(sample))
