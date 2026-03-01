"""
All of the Enums that are used throughout the chardet package.

:author: Dan Blanchard (dan.blanchard@gmail.com)
"""

from enum import Flag, IntEnum, auto


class InputState(IntEnum):
    """
    This enum represents the different states a universal detector can be in.
    """

    PURE_ASCII = 0
    ESC_ASCII = 1
    HIGH_BYTE = 2


class LanguageFilter(Flag):
    """
    This enum represents the different language filters we can apply to a
    ``UniversalDetector``.
    """

    CHINESE_SIMPLIFIED = auto()
    CHINESE_TRADITIONAL = auto()
    JAPANESE = auto()
    KOREAN = auto()
    NON_CJK = auto()
    CHINESE = CHINESE_SIMPLIFIED | CHINESE_TRADITIONAL
    CJK = CHINESE | JAPANESE | KOREAN
    ALL = NON_CJK | CJK


class ProbingState(IntEnum):
    """
    This enum represents the different states a prober can be in.
    """

    DETECTING = 0
    FOUND_IT = 1
    NOT_ME = 2


class MachineState(IntEnum):
    """
    This enum represents the different states a state machine can be in.
    """

    START = 0
    ERROR = 1
    ITS_ME = 2


class SequenceLikelihood(IntEnum):
    """
    This enum represents the likelihood of a character following the previous one.
    """

    NEGATIVE = 0
    UNLIKELY = 1
    LIKELY = 2
    POSITIVE = 3


class CharacterCategory(IntEnum):
    """
    This enum represents the different categories language models for
    ``SingleByteCharsetProber`` put characters into.

    Anything less than DIGIT is considered a letter.
    """

    UNDEFINED = 255
    CONTROL = 254
    SYMBOL = 253
    LINE_BREAK = 252
    DIGIT = 251


class EncodingEra(Flag):
    """
    This enum represents different eras of character encodings, used to filter
    which encodings are considered during detection.

    The numeric values also serve as preference tiers for tie-breaking when
    confidence scores are very close. Lower values = more preferred/modern.

    MODERN_WEB: UTF-8/16/32, Windows-125x, CP874, KOI8-R/U, CJK multi-byte (widely used on the web)
    LEGACY_ISO: ISO-8859-x (legacy but well-known standards)
    LEGACY_MAC: Mac-specific encodings (MacRoman, MacCyrillic, etc.)
    LEGACY_REGIONAL: Uncommon regional/national encodings (KOI8-T, KZ1048, CP1006, etc.)
    DOS: DOS/OEM code pages (CP437, CP850, CP866, etc.)
    MAINFRAME: EBCDIC variants (CP037, CP500, etc.)
    """

    MODERN_WEB = auto()
    LEGACY_ISO = auto()
    LEGACY_MAC = auto()
    LEGACY_REGIONAL = auto()
    DOS = auto()
    MAINFRAME = auto()
    ALL = MODERN_WEB | LEGACY_ISO | LEGACY_MAC | LEGACY_REGIONAL | DOS | MAINFRAME
