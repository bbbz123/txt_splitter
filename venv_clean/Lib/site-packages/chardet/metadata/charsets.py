"""
Metadata about charsets used by our model training code and test file
generationcode. Could be used for other things in the future.
"""

from dataclasses import dataclass

from chardet.enums import EncodingEra, LanguageFilter


@dataclass(frozen=True)
class Charset:
    """Metadata about charsets useful for training models and generating test files."""

    name: str
    is_multi_byte: bool
    encoding_era: EncodingEra
    language_filter: LanguageFilter


CHARSETS = {
    "ASCII": Charset(
        name="ASCII",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "BIG5": Charset(
        name="Big5",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.CHINESE_TRADITIONAL,
    ),
    "CP037": Charset(
        name="CP037",
        is_multi_byte=False,
        encoding_era=EncodingEra.MAINFRAME,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP424": Charset(
        name="CP424",
        is_multi_byte=False,
        encoding_era=EncodingEra.MAINFRAME,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP437": Charset(
        name="CP437",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP500": Charset(
        name="CP500",
        is_multi_byte=False,
        encoding_era=EncodingEra.MAINFRAME,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP720": Charset(
        name="CP720",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_REGIONAL,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP737": Charset(
        name="CP737",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP775": Charset(
        name="CP775",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP850": Charset(
        name="CP850",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP852": Charset(
        name="CP852",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP855": Charset(
        name="CP855",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP856": Charset(
        name="CP856",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP857": Charset(
        name="CP857",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP858": Charset(
        name="CP858",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP860": Charset(
        name="CP860",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP861": Charset(
        name="CP861",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP862": Charset(
        name="CP862",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP863": Charset(
        name="CP863",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP864": Charset(
        name="CP864",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP865": Charset(
        name="CP865",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP866": Charset(
        name="CP866",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP869": Charset(
        name="CP869",
        is_multi_byte=False,
        encoding_era=EncodingEra.DOS,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP874": Charset(
        name="CP874",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP875": Charset(
        name="CP875",
        is_multi_byte=False,
        encoding_era=EncodingEra.MAINFRAME,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP932": Charset(
        name="CP932",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.JAPANESE,
    ),
    "CP949": Charset(
        name="CP949",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.KOREAN,
    ),
    "CP1006": Charset(
        name="CP1006",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_REGIONAL,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP1026": Charset(
        name="CP1026",
        is_multi_byte=False,
        encoding_era=EncodingEra.MAINFRAME,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "CP1125": Charset(
        name="CP1125",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_REGIONAL,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "EUC-JP": Charset(
        name="EUC-JP",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.JAPANESE,
    ),
    "EUC-KR": Charset(
        name="EUC-KR",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.KOREAN,
    ),
    "GB18030": Charset(
        name="GB18030",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.CHINESE_SIMPLIFIED,
    ),
    "HZ-GB-2312": Charset(
        name="HZ-GB-2312",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.CHINESE_SIMPLIFIED,
    ),
    "ISO-2022-JP": Charset(
        name="ISO-2022-JP",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.JAPANESE,
    ),
    "ISO-2022-KR": Charset(
        name="ISO-2022-KR",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.KOREAN,
    ),
    "ISO-8859-1": Charset(
        name="ISO-8859-1",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-2": Charset(
        name="ISO-8859-2",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-3": Charset(
        name="ISO-8859-3",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-4": Charset(
        name="ISO-8859-4",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-5": Charset(
        name="ISO-8859-5",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-6": Charset(
        name="ISO-8859-6",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-7": Charset(
        name="ISO-8859-7",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-8": Charset(
        name="ISO-8859-8",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-9": Charset(
        name="ISO-8859-9",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-10": Charset(
        name="ISO-8859-10",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-11": Charset(
        name="ISO-8859-11",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-13": Charset(
        name="ISO-8859-13",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-14": Charset(
        name="ISO-8859-14",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-15": Charset(
        name="ISO-8859-15",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "ISO-8859-16": Charset(
        name="ISO-8859-16",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "JOHAB": Charset(
        name="Johab",
        is_multi_byte=True,
        encoding_era=EncodingEra.LEGACY_ISO,
        language_filter=LanguageFilter.KOREAN,
    ),
    "KOI8-R": Charset(
        name="KOI8-R",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "KOI8-U": Charset(
        name="KOI8-U",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "KOI8-T": Charset(
        name="KOI8-T",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_REGIONAL,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "KZ1048": Charset(
        name="KZ1048",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_REGIONAL,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "MACCYRILLIC": Charset(
        name="MacCyrillic",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_MAC,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "MACGREEK": Charset(
        name="MacGreek",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_MAC,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "MACICELAND": Charset(
        name="MacIceland",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_MAC,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "MACLATIN2": Charset(
        name="MacLatin2",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_MAC,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "MACROMAN": Charset(
        name="MacRoman",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_MAC,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "MACTURKISH": Charset(
        name="MacTurkish",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_MAC,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "PTCP154": Charset(
        name="PTCP154",
        is_multi_byte=False,
        encoding_era=EncodingEra.LEGACY_REGIONAL,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "SHIFT-JIS": Charset(
        name="Shift-JIS",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.JAPANESE,
    ),
    "TIS-620": Charset(
        name="TIS-620",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "UTF-8": Charset(
        name="UTF-8",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.ALL,
    ),
    "UTF-8-SIG": Charset(
        name="UTF-8-SIG",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.ALL,
    ),
    "UTF-16": Charset(
        name="UTF-16",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.ALL,
    ),
    "UTF-16BE": Charset(
        name="UTF-16BE",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.ALL,
    ),
    "UTF-16LE": Charset(
        name="UTF-16LE",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.ALL,
    ),
    "UTF-32": Charset(
        name="UTF-32",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.ALL,
    ),
    "UTF-32BE": Charset(
        name="UTF-32BE",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.ALL,
    ),
    "UTF-32LE": Charset(
        name="UTF-32LE",
        is_multi_byte=True,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.ALL,
    ),
    "WINDOWS-1250": Charset(
        name="Windows-1250",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "WINDOWS-1251": Charset(
        name="Windows-1251",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "WINDOWS-1252": Charset(
        name="Windows-1252",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "WINDOWS-1253": Charset(
        name="Windows-1253",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "WINDOWS-1254": Charset(
        name="Windows-1254",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "WINDOWS-1255": Charset(
        name="Windows-1255",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "WINDOWS-1256": Charset(
        name="Windows-1256",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "WINDOWS-1257": Charset(
        name="Windows-1257",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
    "WINDOWS-1258": Charset(
        name="Windows-1258",
        is_multi_byte=False,
        encoding_era=EncodingEra.MODERN_WEB,
        language_filter=LanguageFilter.NON_CJK,
    ),
}


_DEFAULT_CHARSET = Charset(
    name="Unknown",
    is_multi_byte=False,
    encoding_era=EncodingEra.MODERN_WEB,
    language_filter=LanguageFilter.ALL,
)


def get_charset(encoding_name: str) -> Charset:
    """
    Get the Charset metadata for a given encoding name.

    :param encoding_name: The encoding name to look up
    :return: The Charset for this encoding, defaults to a MODERN_WEB charset if unknown
    """
    normalized_name = encoding_name.upper().replace("_", "-")
    return CHARSETS.get(normalized_name, _DEFAULT_CHARSET)


def is_unicode_encoding(encoding_name: str) -> bool:
    """
    Check if an encoding is a Unicode encoding (UTF-8, UTF-16, UTF-32).

    :param encoding_name: The encoding name to check
    :return: True if the encoding is Unicode, False otherwise
    """
    normalized_name = encoding_name.upper().replace("_", "-")
    return normalized_name.startswith("UTF-")
