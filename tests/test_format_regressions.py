from __future__ import annotations

import os
import sys
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ebooklib import epub

from core.document_loader import DocumentLoader
from core.parser import TextParser
from core.patterns import build_regexes_from_tokens
from core.split_service import SplitService


def _chapter_settings(output_dir: Path) -> dict:
    return {
        "mode": "Chapter Mode",
        "strategy": "Flat Folder",
        "structure": "Chapter",
        "language": "en",
        "constraint_limit": "5",
        "constraint_comparator": "≈",
        "chunk_break": "Sentence",
        "max_length": "1500",
        "chunk_size": "500",
        "enable_chunking": False,
        "trigger_comparator": "≈",
        "chunk_size_comparator": "≈",
        "include_body": True,
        "skip_toc": True,
        "output_dir": str(output_dir),
    }


def _txt_filenames(output_dir: Path) -> list[str]:
    return sorted(path.name for path in output_dir.glob("*.txt"))


def test_pdf_sample_regression_extracts_and_splits(sample_pdf_path: Path, tmp_path: Path):
    parser = TextParser()
    output_dir = tmp_path / "pdf_out"

    with parser.prepared_document(str(sample_pdf_path)) as prepared:
        assert prepared.source_ext == ".pdf"
        assert prepared.has_native_structure is False

        regexes = build_regexes_from_tokens(["Chapter"], "en")
        chapters, encoding = parser.parse_chapters(prepared.working_text_path, regexes, prepared.encoding)

        assert len(chapters) == 2
        assert "Chapter" in chapters[0]["raw_title"]
        assert "Chapter" in chapters[1]["raw_title"]

        parser.split_file(
            prepared.working_text_path,
            chapters,
            str(output_dir),
            encoding,
            output_mode="Flat Folder",
            include_body=True,
            skip_toc=True,
        )

    out_files = _txt_filenames(output_dir)
    assert len(out_files) == 2
    assert out_files[0].endswith(".txt")
    assert out_files[1].endswith(".txt")


def test_docx_sample_regression_uses_native_headings(sample_docx_path: Path, tmp_path: Path):
    loader = DocumentLoader()
    doc = loader.prepare(str(sample_docx_path))
    try:
        assert doc.source_ext == ".docx"
        assert doc.has_native_structure is True
        assert doc.native_chapters is not None
        assert [chapter["raw_title"] for chapter in doc.native_chapters] == [
            "Book Title",
            "Chapter One",
            "Chapter Two",
        ]
    finally:
        loader.cleanup(doc)

    output_dir = tmp_path / "docx_out"
    service = SplitService(TextParser())
    settings = _chapter_settings(output_dir)
    scan = service.scan_files([str(sample_docx_path)], settings, {})

    assert scan.failed_files == []
    assert str(sample_docx_path) in scan.parsed_chapters

    result = service.split_files([str(sample_docx_path)], settings, {}, scan.parsed_chapters)
    assert result.failed_files == []

    out_files = _txt_filenames(output_dir)
    assert len(out_files) == 3
    assert any("Book Title" in name for name in out_files)


def test_epub_sample_regression_uses_toc_structure(sample_epub_path: Path, tmp_path: Path):
    loader = DocumentLoader()
    doc = loader.prepare(str(sample_epub_path))
    try:
        assert doc.source_ext == ".epub"
        assert doc.has_native_structure is True
        assert doc.native_chapters is not None
        assert [chapter["raw_title"] for chapter in doc.native_chapters] == [
            "Book Title",
            "Chapter One",
            "Chapter Two",
        ]
    finally:
        loader.cleanup(doc)

    output_dir = tmp_path / "epub_out"
    service = SplitService(TextParser())
    settings = _chapter_settings(output_dir)
    scan = service.scan_files([str(sample_epub_path)], settings, {})

    assert scan.failed_files == []
    assert str(sample_epub_path) in scan.parsed_chapters

    result = service.split_files([str(sample_epub_path)], settings, {}, scan.parsed_chapters)
    assert result.failed_files == []

    out_files = _txt_filenames(output_dir)
    assert len(out_files) == 3
    assert any("Chapter One" in name for name in out_files)


def test_epub_toc_fragment_anchors_map_to_inner_heading_lines(tmp_path: Path):
    epub_path = tmp_path / "anchored.epub"
    book = epub.EpubBook()
    book.set_identifier("anchored-book")
    book.set_title("Anchored Book")
    book.set_language("zh")

    chapter = epub.EpubHtml(title="第一章 测试", file_name="chapter.xhtml", lang="zh")
    chapter.content = """
    <html><body>
      <h1>第一章 测试</h1>
      <p>章引言。</p>
      <p id="sec1"></p>
      <h2>第一节 粮粒</h2>
      <p>第一节正文。</p>
      <p id="sec2"></p>
      <h2>第二节 流散</h2>
      <p>第二节正文。</p>
    </body></html>
    """

    book.add_item(chapter)
    book.toc = (
        epub.Link("chapter.xhtml", "第一章 测试", "chapter"),
        (
            epub.Section("第一章 测试"),
            (
                epub.Link("chapter.xhtml#sec1", "第一节 粮粒", "sec1"),
                epub.Link("chapter.xhtml#sec2", "第二节 流散", "sec2"),
            ),
        ),
    )
    book.spine = ["nav", chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(str(epub_path), book)

    loader = DocumentLoader()
    doc = loader.prepare(str(epub_path))
    try:
        assert doc.native_chapters is not None
        assert [chapter["raw_title"] for chapter in doc.native_chapters] == [
            "第一章 测试",
            "第一节 粮粒",
            "第二节 流散",
        ]
        line_starts = [chapter["line_start"] for chapter in doc.native_chapters]
        assert line_starts == sorted(line_starts)
        assert len(set(line_starts)) == 3
    finally:
        loader.cleanup(doc)


def test_epub_toc_url_encoded_href_matches_spine_item(tmp_path: Path):
    epub_path = tmp_path / "encoded_href.epub"
    book = epub.EpubBook()
    book.set_identifier("encoded-href-book")
    book.set_title("Encoded Href Book")
    book.set_language("en")

    chapter = epub.EpubHtml(title="Chapter One", file_name="chapter one.xhtml", lang="en")
    chapter.content = """
    <html><body>
      <h1>Chapter One</h1>
      <p>Intro.</p>
      <p id="sec 1"></p>
      <h2>Section One</h2>
      <p>Section body.</p>
    </body></html>
    """

    book.add_item(chapter)
    book.toc = (
        epub.Link("chapter%20one.xhtml", "Chapter One", "chapter"),
        epub.Link("chapter%20one.xhtml#sec%201", "Section One", "sec1"),
    )
    book.spine = ["nav", chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(str(epub_path), book)

    loader = DocumentLoader()
    doc = loader.prepare(str(epub_path))
    try:
        assert doc.native_chapters is not None
        assert [chapter["raw_title"] for chapter in doc.native_chapters] == [
            "Chapter One",
            "Section One",
        ]
        assert doc.native_chapters[0]["line_start"] < doc.native_chapters[1]["line_start"]
    finally:
        loader.cleanup(doc)


def test_markdown_chapter_split_end_to_end(sample_markdown_path: Path, tmp_path: Path):
    output_dir = tmp_path / "markdown_out"
    service = SplitService(TextParser())
    settings = _chapter_settings(output_dir)

    scan = service.scan_files([str(sample_markdown_path)], settings, {})
    assert scan.failed_files == []
    assert str(sample_markdown_path) in scan.parsed_chapters

    chapters = scan.parsed_chapters[str(sample_markdown_path)]["en"]
    assert [chapter["raw_title"] for chapter in chapters] == [
        "Book Title",
        "Chapter One",
        "Chapter Two",
    ]

    result = service.split_files([str(sample_markdown_path)], settings, {}, scan.parsed_chapters)
    assert result.failed_files == []

    out_files = _txt_filenames(output_dir)
    assert len(out_files) == 3
    assert any("Chapter Two" in name for name in out_files)
