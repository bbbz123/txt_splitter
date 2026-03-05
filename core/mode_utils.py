"""Shared mode helpers used by GUI and parser.

Keeping mode keyword matching centralized avoids drift between UI labels
and backend behavior.
"""

from __future__ import annotations

from typing import Tuple

# Constraint split mode detection keywords
CONSTRAINT_MODE_KEYWORDS: Tuple[str, ...] = (
    "KB",
    "大小",
    "字数",
    "Word Count",
    "行数",
    "Line Count",
    "段落",
    "段落数",
    "Paragraph Count",
    "Paragraph",
    "Size",
)

SIZE_MODE_KEYWORDS: Tuple[str, ...] = ("KB", "Size", "大小")
WORD_MODE_KEYWORDS: Tuple[str, ...] = ("字数", "Word Count", "Words")
LINE_MODE_KEYWORDS: Tuple[str, ...] = ("行数", "Line Count", "Lines")
PARAGRAPH_MODE_KEYWORDS: Tuple[str, ...] = ("段落", "段落数", "Paragraph Count", "Paragraphs", "Paragraph")
CHAPTER_MODE_KEYWORDS: Tuple[str, ...] = ("章节模式", "章节", "Chapter", "Regex")


def _has_any_keyword(mode: str, keywords: Tuple[str, ...]) -> bool:
    return any(k in mode for k in keywords)


def is_constraint_mode(mode: str) -> bool:
    return _has_any_keyword(mode, CONSTRAINT_MODE_KEYWORDS)


def is_size_mode(mode: str) -> bool:
    return _has_any_keyword(mode, SIZE_MODE_KEYWORDS)


def is_word_mode(mode: str) -> bool:
    return _has_any_keyword(mode, WORD_MODE_KEYWORDS)


def is_line_mode(mode: str) -> bool:
    return _has_any_keyword(mode, LINE_MODE_KEYWORDS)


def is_paragraph_mode(mode: str) -> bool:
    return _has_any_keyword(mode, PARAGRAPH_MODE_KEYWORDS)


def needs_secondary_constraint_chunking(mode: str) -> bool:
    return is_line_mode(mode) or is_paragraph_mode(mode)


def is_chapter_mode(mode: str) -> bool:
    return _has_any_keyword(mode, CHAPTER_MODE_KEYWORDS)
