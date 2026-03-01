"""
core/patterns.py — Multi-language regex pattern registry.

Each language defines its own LanguagePatterns instance containing:
- Preset regex patterns for the GUI dropdown
- Keywords and weights for hierarchical structure analysis
- Heading regex for detecting chapter/section headings
- Token-to-regex builder for user-defined keywords
- TOC detection patterns
- "One" equivalents for parent-child reset detection

To add a new language, implement a _build_xxx_patterns() function
and register it in LANGUAGE_REGISTRY.
"""

import re
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class LanguagePatterns:
    """Encapsulates all regex-related configuration for a single language."""
    lang_id: str
    display_name: str

    # Preset regex groups shown in the GUI dropdown
    preset_patterns: dict[str, str]

    # Keywords for analyze_structure (ordered from high to low level)
    structure_keywords: list[str]
    # Fallback weight map for tie-breaking in parent-child detection
    keywords_weight_map: dict[str, int]

    # Regex to detect headings like "第X章" or "Chapter X"
    heading_regex: re.Pattern  # type: ignore[type-arg]

    # Extract (keyword, number_str) from a heading match
    extract_heading: Callable[[re.Match], tuple[str, str]]  # type: ignore[type-arg]

    # TOC detection
    toc_header_regex: re.Pattern  # type: ignore[type-arg]
    toc_footer_regex: Optional[re.Pattern] = None  # type: ignore[type-arg]

    # Set of strings that represent "1" / "first" for reset detection
    ones_set: set[str] = field(default_factory=set)

    # Build a regex from a UI token (e.g. "章" → r'^\s*第[\d零一二...]+章.*')
    build_regex_from_token: Callable[[str], str] = field(default=lambda t: '')  # type: ignore


# ──────────────────────────────────────────────
#  Chinese Language Patterns
# ──────────────────────────────────────────────

def _zh_extract_heading(m: re.Match) -> tuple[str, str]:  # type: ignore[type-arg]
    """Extract (keyword, number_str) from a Chinese heading match."""
    if m.group(1):
        return m.group(3), m.group(2)  # "第X章" → kw="章", num="X"
    elif m.group(4):
        return m.group(5), m.group(6)  # "章X" → kw="章", num="X"
    elif m.group(7):
        return '#Digit', m.group(7)    # "12" -> kw="#Digit", num="12"
    return '', ''


def _zh_build_regex_from_token(token: str) -> str:
    """Build a regex from a Chinese UI token like '章', '分篇', '"一"'."""
    token_stripped = token.strip()
    if token_stripped.lower() in ('1', '#digit'):
        return r'^\s*\d+\s*$'
        
    if (token_stripped.startswith('"') and token_stripped.endswith('"')) or \
       (token_stripped.startswith('\u201c') and token_stripped.endswith('\u201d')):
        inner = token_stripped[1 : len(token_stripped) - 1]  # strip surrounding quotes
        if inner == '一':
            return r'^\s*[零一二三四五六七八九十百千万]+[、\s\.:：].*'
        elif inner == '1':
            return r'^\s*\d+[、\s\.:：].*'
        elif inner.upper() in ['I', 'V', 'X']:
            return r'^\s*[IVXLCDM]+[、\s\.:：].*'
        elif inner.islower() or inner.isupper():
            return r'^\s*[a-zA-Z][、\s\.:：].*'
        else:
            return rf'^\s*{re.escape(inner)}.*'
    else:
        safe_token = re.escape(token)
        if len(token) == 1:
            return rf'^\s*第[\d零一二三四五六七八九十百千万]+{safe_token}.*'
        else:
            return (
                rf'^\s*(?:第[\d零一二三四五六七八九十百千万]+\s*{safe_token}'
                rf'|{safe_token}\s*[\d零一二三四五六七八九十百千万]+).*'
            )


def _build_chinese_patterns() -> LanguagePatterns:
    all_keywords = [
        '分卷', '分部', '分编', '分篇',
        '上篇', '中篇', '下篇',
        '卷', '部', '集', '册',
        '编', '篇',
        '章', '回',
        '节', '折', '幕',
        '条', '款', '项',
    ]

    keywords_weight_map = {
        '卷': 10, '部': 10, '集': 10,
        '册': 12,
        '分卷': 15, '分部': 15,
        '编': 20, '篇': 20,
        '分编': 25, '分篇': 25,
        '上篇': 22, '下篇': 22, '中篇': 22,
        '章': 30, '回': 30,
        '节': 40, '折': 40, '幕': 40,
        '条': 50,
        '款': 60,
        '项': 70,
        '#Digit': 30,  # Pure Arabic digits at chapter-level by default
    }

    kw_pattern = '|'.join(re.escape(k) for k in all_keywords)
    heading_re = re.compile(
        rf'^[\s\u3000]*(第([零一二三四五六七八九十百千万\d]+)\s*({kw_pattern}))'
        rf'|^[\s\u3000]*(({kw_pattern})\s*([零一二三四五六七八九十百千万\d]+))'
        rf'|^\s*(\d+)\s*$'
    )

    preset = {
        "Level 1: Volume/Book (卷/编/册/部/集)": r'^\s*第[零一二三四五六七八九十百千万0-9]+[卷编册部集].*',
        "Level 2: Part/Section (篇/分编)": r'^\s*第[零一二三四五六七八九十百千万0-9]+[篇分].*',
        "Level 3: Chapter (章/回/节)": r'^\s*第[零一二三四五六七八九十百千万0-9]+[章回节].*',
        "Common All (卷/编/篇/章/回/节)": r'^\s*(第[零一二三四五六七八九十百千万0-9]+[卷编册部集篇分章回节].*)',
        "Law Article (第一条)": r'^\s*第[零一二三四五六七八九十百千万0-9]+条.*',
        "Digit Only (1, 2, 3...)": r'^\s*\d+\s*$',
        "Digit (1. xxx)": r'^\s*\d+[\.\s、].*',
    }

    toc_header_re = re.compile(
        r'^[\s\u3000]*(总目录|目\s*录|CONTENTS|TABLE\s+OF\s+CONTENTS)',
        re.IGNORECASE
    )
    toc_footer_re = re.compile(r'(返回总目录|返回目录)', re.IGNORECASE)

    ones = {'1', '01', '一', '壹', '零', '〇', '0'}

    return LanguagePatterns(
        lang_id='zh',
        display_name='中文',
        preset_patterns=preset,
        structure_keywords=all_keywords + ['#Digit'],
        keywords_weight_map=keywords_weight_map,
        heading_regex=heading_re,
        extract_heading=_zh_extract_heading,
        toc_header_regex=toc_header_re,
        toc_footer_regex=toc_footer_re,
        ones_set=ones,
        build_regex_from_token=_zh_build_regex_from_token,
    )


# ──────────────────────────────────────────────
#  English Language Patterns
# ──────────────────────────────────────────────

# English number words for regex matching
_EN_NUMBER_WORDS = (
    'One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|'
    'Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|'
    'Seventeen|Eighteen|Nineteen|Twenty|'
    'Twenty[- ]?One|Twenty[- ]?Two|Twenty[- ]?Three|Twenty[- ]?Four|'
    'Twenty[- ]?Five|Twenty[- ]?Six|Twenty[- ]?Seven|Twenty[- ]?Eight|'
    'Twenty[- ]?Nine|Thirty|Forty|Fifty|Sixty|Seventy|Eighty|Ninety|'
    'Hundred'
)
_EN_ROMAN = r'[IVXLCDM]+'
# Strict Roman pattern: only valid sequences, avoids false matches on words like "I" in prose
# Must be at least 2 chars, OR single valid numerals (I, V, X, L, C, D, M)
_EN_ROMAN_STRICT = r'(?:M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{1,3})|M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{1,3})|M{0,3}(?:CM|CD|D?C{1,3})|M{1,3}|(?:IX|IV|V?I{2,3})|V|X{1,3}L?|L|XC|XL|CD|CM|D)'
_EN_DIGIT = r'\d+'
_EN_NUM = rf'(?:{_EN_DIGIT}|{_EN_ROMAN}|{_EN_NUMBER_WORDS})'

# English structural keywords (ordered high → low level)
_EN_KEYWORDS = [
    'Book', 'Volume',
    'Part',
    'Chapter',
    'Section',
    'Act', 'Scene',
]

# Fixed-title keywords that stand alone (no numbering)
_EN_FIXED_TITLES = [
    'Prologue', 'Epilogue', 'Preface', 'Introduction',
    'Foreword', 'Afterword', 'Appendix', 'Conclusion',
    'Interlude', 'Intermission',
]


def _en_extract_heading(m: re.Match) -> tuple[str, str]:  # type: ignore[type-arg]
    """Extract (keyword, number_str) from an English heading match.
    
    Groups layout of the heading_re:
      branch 1 – keyword + number:  group(1)=keyword, group(2)=number
      branch 2 – fixed title:       group(3)=title
      branch 3 – standalone roman:  group(4)=roman
      branch 4 – standalone digit:  group(5)=digit
    """
    # Branch 1: "Chapter 3", "Part IV"
    if m.group(1) and m.group(2):
        return m.group(1).title(), m.group(2)
    # Branch 2: "Prologue", "Epilogue"
    if m.group(3):
        return m.group(3).title(), '0'
    # Branch 3: standalone Roman numeral line  "III"
    if m.group(4):
        return '#Roman', m.group(4)
    # Branch 4: standalone digit line  "12"
    if m.group(5):
        return '#Digit', m.group(5)
    return '', ''


def _en_build_regex_from_token(token: str) -> str:
    """Build a regex from an English UI token like 'Chapter', 'Part', 'Prologue'."""
    token_stripped = token.strip()

    # Handle quoted tokens for literal matching
    if (token_stripped.startswith('"') and token_stripped.endswith('"')) or \
       (token_stripped.startswith('\u201c') and token_stripped.endswith('\u201d')):
        inner = token_stripped[1 : len(token_stripped) - 1]  # strip surrounding quotes
        return rf'^\s*{re.escape(inner)}.*'

    # Check if it's a fixed title keyword
    lower = token_stripped.lower()
    for ft in _EN_FIXED_TITLES:
        if lower == ft.lower():
            return rf'^\s*{re.escape(ft)}\b.*'

    if lower in ('i', '#roman'):
        return rf'^\s*{_EN_ROMAN_STRICT}\s*$'
    if lower in ('1', '#digit'):
        return r'^\s*\d+\s*$'

    # Check if it's a structural keyword (Chapter, Part, etc.)
    for kw in _EN_KEYWORDS:
        if lower == kw.lower():
            return (
                rf'^\s*{re.escape(kw)}\s+'
                rf'(?:\d+|[IVXLCDM]+|{_EN_NUMBER_WORDS})\b.*'
            )

    # Fallback: treat as literal prefix
    safe = re.escape(token_stripped)
    return rf'^\s*{safe}\b.*'


def _build_english_patterns() -> LanguagePatterns:
    kw_pattern = '|'.join(re.escape(k) for k in _EN_KEYWORDS)
    fixed_pattern = '|'.join(re.escape(k) for k in _EN_FIXED_TITLES)

    # 4-branch heading regex:
    #   branch 1: keyword + number   (Chapter 3, Part IV, Book One)
    #   branch 2: fixed title alone   (Prologue, Epilogue)
    #   branch 3: standalone roman    (III, XIV)
    #   branch 4: standalone digit    (12, 3)
    heading_re = re.compile(
        rf'^\s*({kw_pattern})\s+({_EN_NUM})\b'
        rf'|^\s*({fixed_pattern})\s*$'
        rf'|^\s*({_EN_ROMAN_STRICT})\s*$'
        rf'|^\s*(\d+)\s*$',
        re.IGNORECASE | re.MULTILINE
    )

    preset = {
        "All Levels (Book/Part/Chapter)": (
            r"^\s*(?:(?:Chapter|Section|Part|Book|Vol|Volume|PROLOGUE|EPILOGUE)\s+(?:[0-9IVXLCDM]+|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen|Nineteen|Twenty|Twenty[- ]?One|Twenty[- ]?Two|Twenty[- ]?Three|Twenty[- ]?Four|Twenty[- ]?Five|Twenty[- ]?Six|Twenty[- ]?Seven|Twenty[- ]?Eight|Twenty[- ]?Nine|Thirty|Forty|Fifty|Sixty|Seventy|Eighty|Ninety|Hundred)|CHAPTER\s+[0-9IVXLCDM]+|Chapter\s+[0-9IVXLCDM]+|Section\s+[0-9]+|PART|Part\s+[IVXLCDM]+|[0-9IVXLCDM]+\.?\s+[A-Z][A-Za-z\s]+).*?"
            r"|^\s*CHAPTER\s+[0-9IVXLCDM]+.*"
            r"|^\s*Chapter\s+[0-9IVXLCDM]+.*"
            r"|^\s*[0-9]+\s+[A-Z].*" # 1 Discovery
            r"|^\s*[IVXLCDM]+\.\s+[A-Z].*" # I. Introduction
        ),
        "Chapter Only": (
            rf'^\s*Chapter\s+'
            rf'(?:\d+|[IVXLCDM]+|{_EN_NUMBER_WORDS})\b.*'
        ),
        "Part Only": (
            rf'(?i)^\s*Part\s+'
            rf'(?:\d+|[IVXLCDM]+|{_EN_NUMBER_WORDS})\b.*'
        ),
        "Book Only": (
            rf'(?i)^\s*Book\s+'
            rf'(?:\d+|[IVXLCDM]+|{_EN_NUMBER_WORDS})\b.*'
        ),
        "Prologue/Epilogue/Special": (
            rf'(?i)^\s*(?:{fixed_pattern})\s*$'
        ),
        "Act/Scene (Drama)": (
            r'(?i)^\s*(?:Act|Scene)\s+'
            r'(?:\d+|[IVXLCDM]+)\b.*'
        ),
        "Roman Numeral (I, II, III...)": rf'^\s*{_EN_ROMAN_STRICT}\s*$',
        "Digit Only (1, 2, 3...)": r'^\s*\d+\s*$',
        "Digit (1. xxx)": r'^\s*\d+[\.\s].*',
    }

    keywords_weight_map = {
        'Book': 10, 'Volume': 10,
        'Part': 20,
        'Chapter': 30,
        'Section': 40,
        'Act': 25, 'Scene': 35,
        '#Roman': 30, '#Digit': 30,  # standalone numbers treated as chapter-level
    }

    toc_header_re = re.compile(
        r'(?i)^\s*(Table\s+of\s+Contents|Contents)\s*$'
    )

    ones = {
        '1', '01', '0',
        'One', 'one', 'ONE',
        'I', 'i',
        'First', 'first',
    }

    return LanguagePatterns(
        lang_id='en',
        display_name='English',
        preset_patterns=preset,
        structure_keywords=_EN_KEYWORDS + ['#Roman', '#Digit'],
        keywords_weight_map=keywords_weight_map,
        heading_regex=heading_re,
        extract_heading=_en_extract_heading,
        toc_header_regex=toc_header_re,
        toc_footer_regex=None,
        ones_set=ones,
        build_regex_from_token=_en_build_regex_from_token,
    )


# ──────────────────────────────────────────────
#  Language Registry
# ──────────────────────────────────────────────

LANGUAGE_REGISTRY: dict[str, LanguagePatterns] = {
    'zh': _build_chinese_patterns(),
    'en': _build_english_patterns(),
}


def get_language(lang_id: str) -> LanguagePatterns:
    """Get a registered language by its ID. Raises KeyError if not found."""
    return LANGUAGE_REGISTRY[lang_id]


def get_all_languages() -> list[LanguagePatterns]:
    """Return all registered languages."""
    return list(LANGUAGE_REGISTRY.values())


def detect_language(text_sample: str) -> str:
    """
    Auto-detect the primary language of a text sample.
    """
    langs = detect_all_languages(text_sample)
    return langs[0] if langs else 'zh'


def detect_all_languages(text_sample: str) -> list[str]:
    """
    Multilingual Detection System (Heuristics by bbbz123).
    Analyzes character distribution and returns a list of detected language codes.
    """
    if not text_sample:
        return ['zh']

    # Count CJK vs Latin characters
    # In some books, one language might have a very long preface.
    # We use a larger sample to ensure we catch all languages.
    sample = text_sample[0:50000] 
    cjk_count = sum(1 for ch in sample if '\u4e00' <= ch <= '\u9fff')
    latin_count = sum(1 for ch in sample if 'a' <= ch.lower() <= 'z')
    
    found = []
    
    # If there's a significant amount of CJK, it's definitely Chinese
    if cjk_count > 50: 
        found.append('zh')
    
    # If there's a significant amount of Latin, it's definitely English/French/etc.
    if latin_count > 50: # Lowered threshold slightly
        found.append('en')
        
    # If nothing detected, default to 'zh'
    if not found:
        return ['zh']
        
    # Sort so the one with more characters is first
    if 'zh' in found and 'en' in found:
        # CJK chars are "heavier" in meaning.
        if cjk_count * 2.5 < latin_count: # If English is significantly more prevalent
            return ['en', 'zh']
        return ['zh', 'en']
        
    return found


def build_regexes_from_tokens(tokens: list[str], lang_id: str) -> list[str]:
    """
    Convert a list of UI tokens to regex patterns using the specified language.
    This replaces the old gui/app.py build_regex_from_token + get_regexes_from_ui.
    """
    lang = get_language(lang_id)
    regexes = []
    for t in tokens:
        t = t.strip()
        if t:
            regexes.append(lang.build_regex_from_token(t))
    return [r for r in regexes if r]
