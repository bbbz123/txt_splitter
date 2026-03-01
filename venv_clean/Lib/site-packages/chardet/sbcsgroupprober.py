######################## BEGIN LICENSE BLOCK ########################
# The Original Code is Mozilla Universal charset detector code.
#
# The Initial Developer of the Original Code is
# Netscape Communications Corporation.
# Portions created by the Initial Developer are Copyright (C) 2001
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Mark Pilgrim - port to Python
#   Shy Shalom - original C code
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, see
# <https://www.gnu.org/licenses/>.
######################### END LICENSE BLOCK #########################

import re
from typing import Union

from .charsetgroupprober import CharSetGroupProber
from .enums import EncodingEra, LanguageFilter, ProbingState
from .hebrewprober import HebrewProber
from .langarabicmodel import (
    CP720_ARABIC_MODEL,
    CP864_ARABIC_MODEL,
    ISO_8859_6_ARABIC_MODEL,
    WINDOWS_1256_ARABIC_MODEL,
)
from .langbelarusianmodel import (
    CP866_BELARUSIAN_MODEL,
    ISO_8859_5_BELARUSIAN_MODEL,
    MACCYRILLIC_BELARUSIAN_MODEL,
    WINDOWS_1251_BELARUSIAN_MODEL,
)
from .langbretonmodel import (
    CP037_BRETON_MODEL,
    CP500_BRETON_MODEL,
    ISO_8859_14_BRETON_MODEL,
)
from .langbulgarianmodel import (
    CP855_BULGARIAN_MODEL,
    ISO_8859_5_BULGARIAN_MODEL,
    MACCYRILLIC_BULGARIAN_MODEL,
    WINDOWS_1251_BULGARIAN_MODEL,
)
from .langcroatianmodel import (
    CP852_CROATIAN_MODEL,
    ISO_8859_2_CROATIAN_MODEL,
    ISO_8859_16_CROATIAN_MODEL,
    MACLATIN2_CROATIAN_MODEL,
    WINDOWS_1250_CROATIAN_MODEL,
)
from .langczechmodel import (
    ISO_8859_2_CZECH_MODEL,
    WINDOWS_1250_CZECH_MODEL,
)
from .langdanishmodel import (
    CP037_DANISH_MODEL,
    CP500_DANISH_MODEL,
    CP850_DANISH_MODEL,
    CP858_DANISH_MODEL,
    CP865_DANISH_MODEL,
    ISO_8859_1_DANISH_MODEL,
    ISO_8859_15_DANISH_MODEL,
    MACROMAN_DANISH_MODEL,
    WINDOWS_1252_DANISH_MODEL,
)
from .langdutchmodel import (
    CP037_DUTCH_MODEL,
    CP500_DUTCH_MODEL,
    CP850_DUTCH_MODEL,
    CP858_DUTCH_MODEL,
    ISO_8859_1_DUTCH_MODEL,
    ISO_8859_15_DUTCH_MODEL,
    MACROMAN_DUTCH_MODEL,
    WINDOWS_1252_DUTCH_MODEL,
)
from .langenglishmodel import (
    CP037_ENGLISH_MODEL,
    CP437_ENGLISH_MODEL,
    CP500_ENGLISH_MODEL,
    CP850_ENGLISH_MODEL,
    CP858_ENGLISH_MODEL,
    ISO_8859_1_ENGLISH_MODEL,
    ISO_8859_15_ENGLISH_MODEL,
    MACROMAN_ENGLISH_MODEL,
    WINDOWS_1252_ENGLISH_MODEL,
)
from .langesperantomodel import ISO_8859_3_ESPERANTO_MODEL
from .langestonianmodel import (
    CP775_ESTONIAN_MODEL,
    ISO_8859_4_ESTONIAN_MODEL,
    ISO_8859_13_ESTONIAN_MODEL,
    WINDOWS_1257_ESTONIAN_MODEL,
)
from .langfarsimodel import (
    ISO_8859_6_FARSI_MODEL,
    WINDOWS_1256_FARSI_MODEL,
)
from .langfinnishmodel import (
    CP037_FINNISH_MODEL,
    CP500_FINNISH_MODEL,
    CP850_FINNISH_MODEL,
    CP858_FINNISH_MODEL,
    ISO_8859_1_FINNISH_MODEL,
    ISO_8859_15_FINNISH_MODEL,
    MACROMAN_FINNISH_MODEL,
    WINDOWS_1252_FINNISH_MODEL,
)
from .langfrenchmodel import (
    CP037_FRENCH_MODEL,
    CP500_FRENCH_MODEL,
    CP850_FRENCH_MODEL,
    CP858_FRENCH_MODEL,
    CP863_FRENCH_MODEL,
    ISO_8859_1_FRENCH_MODEL,
    ISO_8859_15_FRENCH_MODEL,
    MACROMAN_FRENCH_MODEL,
    WINDOWS_1252_FRENCH_MODEL,
)
from .langgermanmodel import (
    CP037_GERMAN_MODEL,
    CP500_GERMAN_MODEL,
    CP850_GERMAN_MODEL,
    CP858_GERMAN_MODEL,
    ISO_8859_1_GERMAN_MODEL,
    ISO_8859_15_GERMAN_MODEL,
    MACROMAN_GERMAN_MODEL,
    WINDOWS_1252_GERMAN_MODEL,
)
from .langgreekmodel import (
    CP737_GREEK_MODEL,
    CP869_GREEK_MODEL,
    CP875_GREEK_MODEL,
    ISO_8859_7_GREEK_MODEL,
    MACGREEK_GREEK_MODEL,
    WINDOWS_1253_GREEK_MODEL,
)
from .langhebrewmodel import (
    CP424_HEBREW_MODEL,
    CP856_HEBREW_MODEL,
    CP862_HEBREW_MODEL,
    ISO_8859_8_HEBREW_MODEL,
    WINDOWS_1255_HEBREW_MODEL,
)
from .langhungarianmodel import (
    CP852_HUNGARIAN_MODEL,
    ISO_8859_2_HUNGARIAN_MODEL,
    ISO_8859_16_HUNGARIAN_MODEL,
    MACLATIN2_HUNGARIAN_MODEL,
    WINDOWS_1250_HUNGARIAN_MODEL,
)
from .langicelandicmodel import (
    CP037_ICELANDIC_MODEL,
    CP500_ICELANDIC_MODEL,
    CP861_ICELANDIC_MODEL,
    ISO_8859_1_ICELANDIC_MODEL,
    ISO_8859_10_ICELANDIC_MODEL,
    MACICELAND_ICELANDIC_MODEL,
)
from .langindonesianmodel import (
    CP037_INDONESIAN_MODEL,
    CP500_INDONESIAN_MODEL,
    ISO_8859_1_INDONESIAN_MODEL,
    MACROMAN_INDONESIAN_MODEL,
    WINDOWS_1252_INDONESIAN_MODEL,
)
from .langirishmodel import (
    CP037_IRISH_MODEL,
    CP500_IRISH_MODEL,
    ISO_8859_14_IRISH_MODEL,
)
from .langitalianmodel import (
    CP037_ITALIAN_MODEL,
    CP500_ITALIAN_MODEL,
    CP850_ITALIAN_MODEL,
    CP858_ITALIAN_MODEL,
    ISO_8859_1_ITALIAN_MODEL,
    ISO_8859_15_ITALIAN_MODEL,
    MACROMAN_ITALIAN_MODEL,
    WINDOWS_1252_ITALIAN_MODEL,
)
from .langkazakhmodel import (
    KZ1048_KAZAKH_MODEL,
    PTCP154_KAZAKH_MODEL,
)
from .langlatvianmodel import (
    CP775_LATVIAN_MODEL,
    ISO_8859_4_LATVIAN_MODEL,
    ISO_8859_13_LATVIAN_MODEL,
    WINDOWS_1257_LATVIAN_MODEL,
)
from .langlithuanianmodel import (
    CP775_LITHUANIAN_MODEL,
    ISO_8859_4_LITHUANIAN_MODEL,
    ISO_8859_13_LITHUANIAN_MODEL,
    WINDOWS_1257_LITHUANIAN_MODEL,
)
from .langmacedonianmodel import (
    CP855_MACEDONIAN_MODEL,
    ISO_8859_5_MACEDONIAN_MODEL,
    MACCYRILLIC_MACEDONIAN_MODEL,
    WINDOWS_1251_MACEDONIAN_MODEL,
)
from .langmalaymodel import (
    CP037_MALAY_MODEL,
    CP500_MALAY_MODEL,
    ISO_8859_1_MALAY_MODEL,
    MACROMAN_MALAY_MODEL,
    WINDOWS_1252_MALAY_MODEL,
)
from .langmaltesemodel import ISO_8859_3_MALTESE_MODEL
from .langnorwegianmodel import (
    CP037_NORWEGIAN_MODEL,
    CP500_NORWEGIAN_MODEL,
    CP850_NORWEGIAN_MODEL,
    CP858_NORWEGIAN_MODEL,
    CP865_NORWEGIAN_MODEL,
    ISO_8859_1_NORWEGIAN_MODEL,
    ISO_8859_15_NORWEGIAN_MODEL,
    MACROMAN_NORWEGIAN_MODEL,
    WINDOWS_1252_NORWEGIAN_MODEL,
)
from .langpolishmodel import (
    CP852_POLISH_MODEL,
    ISO_8859_2_POLISH_MODEL,
    ISO_8859_16_POLISH_MODEL,
    MACLATIN2_POLISH_MODEL,
    WINDOWS_1250_POLISH_MODEL,
)
from .langportuguesemodel import (
    CP037_PORTUGUESE_MODEL,
    CP500_PORTUGUESE_MODEL,
    CP850_PORTUGUESE_MODEL,
    CP858_PORTUGUESE_MODEL,
    CP860_PORTUGUESE_MODEL,
    ISO_8859_1_PORTUGUESE_MODEL,
    ISO_8859_15_PORTUGUESE_MODEL,
    MACROMAN_PORTUGUESE_MODEL,
    WINDOWS_1252_PORTUGUESE_MODEL,
)
from .langromanianmodel import (
    CP852_ROMANIAN_MODEL,
    ISO_8859_2_ROMANIAN_MODEL,
    ISO_8859_16_ROMANIAN_MODEL,
    MACLATIN2_ROMANIAN_MODEL,
    WINDOWS_1250_ROMANIAN_MODEL,
)
from .langrussianmodel import (
    CP855_RUSSIAN_MODEL,
    CP866_RUSSIAN_MODEL,
    ISO_8859_5_RUSSIAN_MODEL,
    KOI8_R_RUSSIAN_MODEL,
    MACCYRILLIC_RUSSIAN_MODEL,
    WINDOWS_1251_RUSSIAN_MODEL,
)
from .langscottishgaelicmodel import (
    CP037_SCOTTISH_GAELIC_MODEL,
    CP500_SCOTTISH_GAELIC_MODEL,
    ISO_8859_14_SCOTTISH_GAELIC_MODEL,
)
from .langserbianmodel import (
    CP855_SERBIAN_MODEL,
    ISO_8859_5_SERBIAN_MODEL,
    MACCYRILLIC_SERBIAN_MODEL,
    WINDOWS_1251_SERBIAN_MODEL,
)
from .langslovakmodel import (
    CP852_SLOVAK_MODEL,
    ISO_8859_2_SLOVAK_MODEL,
    ISO_8859_16_SLOVAK_MODEL,
    MACLATIN2_SLOVAK_MODEL,
    WINDOWS_1250_SLOVAK_MODEL,
)
from .langslovenemodel import (
    CP852_SLOVENE_MODEL,
    ISO_8859_2_SLOVENE_MODEL,
    ISO_8859_16_SLOVENE_MODEL,
    MACLATIN2_SLOVENE_MODEL,
    WINDOWS_1250_SLOVENE_MODEL,
)
from .langspanishmodel import (
    CP037_SPANISH_MODEL,
    CP500_SPANISH_MODEL,
    CP850_SPANISH_MODEL,
    CP858_SPANISH_MODEL,
    ISO_8859_1_SPANISH_MODEL,
    ISO_8859_15_SPANISH_MODEL,
    MACROMAN_SPANISH_MODEL,
    WINDOWS_1252_SPANISH_MODEL,
)
from .langswedishmodel import (
    CP037_SWEDISH_MODEL,
    CP500_SWEDISH_MODEL,
    CP850_SWEDISH_MODEL,
    CP858_SWEDISH_MODEL,
    ISO_8859_1_SWEDISH_MODEL,
    ISO_8859_15_SWEDISH_MODEL,
    MACROMAN_SWEDISH_MODEL,
    WINDOWS_1252_SWEDISH_MODEL,
)
from .langtajikmodel import KOI8_T_TAJIK_MODEL
from .langthaimodel import (
    CP874_THAI_MODEL,
    ISO_8859_11_THAI_MODEL,
    TIS_620_THAI_MODEL,
)
from .langturkishmodel import (
    CP857_TURKISH_MODEL,
    CP1026_TURKISH_MODEL,
    ISO_8859_3_TURKISH_MODEL,
    ISO_8859_9_TURKISH_MODEL,
    MACTURKISH_TURKISH_MODEL,
    WINDOWS_1254_TURKISH_MODEL,
)
from .langukrainianmodel import (
    CP1125_UKRAINIAN_MODEL,
    ISO_8859_5_UKRAINIAN_MODEL,
    KOI8_U_UKRAINIAN_MODEL,
    MACCYRILLIC_UKRAINIAN_MODEL,
    WINDOWS_1251_UKRAINIAN_MODEL,
)
from .langvietnamesemodel import WINDOWS_1258_VIETNAMESE_MODEL
from .langwelshmodel import (
    CP037_WELSH_MODEL,
    CP500_WELSH_MODEL,
    ISO_8859_14_WELSH_MODEL,
)
from .sbcharsetprober import SingleByteCharSetProber

# Byte pattern detectors for single-byte encoding disambiguation
# Bytes in 0x80-0x9F range have different meanings in different encoding families:
# - Windows encodings: Smart quotes, dashes, currency symbols (printable punctuation)
# - Mac encodings: Accented letters and diacriticals (printable letters)
# - ISO-8859-x: Control characters (C1 control codes, mostly unprintable)

# Detect any byte in the Windows/Mac range
WIN_BYTE_DETECTOR = re.compile(b"[\x80-\x9f]")

# Detect Mac-only letter bytes for Latin encodings (letters in Mac, control/punct in Win/ISO)
MAC_LATIN_ONLY_LETTER_DETECTOR = re.compile(b"[\x81\x8d\x8f\x90\x92\x9d]")

# Detect MacCyrillic-only letter bytes (Cyrillic letters in Mac, punctuation in Windows-1251)
MAC_CYRILLIC_ONLY_LETTER_DETECTOR = re.compile(
    b"[\x82\x84\x85\x86\x87\x88\x89\x8b\x91\x92\x93\x94\x95\x96\x97\x99\x9b]"
)

# Detect Mac letter bytes appearing between word characters (suggests Mac encoding)
MAC_LETTER_IN_WORD_DETECTOR = re.compile(b"[a-zA-Z][\x80-\x9f][a-zA-Z]")

# Detect Euro sign (0xA4 in ISO-8859-15, but generic currency ¤ in ISO-8859-1)
EURO_SIGN_DETECTOR = re.compile(b"\xa4")

# Latin encodings where Mac=letters and Windows=punctuation in 0x80-0x9F
CONFUSED_LATIN_ENCODINGS = frozenset({
    "macroman",
    "windows-1252",
    "iso-8859-1",
    "iso-8859-15",
    "macgreek",
    "windows-1253",
    "iso-8859-7",
    "macturkish",
    "windows-1254",
    "iso-8859-9",
    "iso-8859-3",  # Turkish/Maltese/Esperanto (also works with MacTurkish/Win-1254)
    "maciceland",
    "iso-8859-10",
    "iso-8859-14",
})

# Central European encodings where Mac=letters and Windows=punctuation in 0x80-0x9F
CONFUSED_CENTRAL_EUROPEAN_ENCODINGS = frozenset({
    "maclatin2",
    "windows-1250",
    "iso-8859-2",
    "iso-8859-16",  # Southeast European/Romanian (close to Latin-2)
})

# Cyrillic encodings where Mac=letters and Windows=punctuation in 0x80-0x9F
CONFUSED_CYRILLIC_ENCODINGS = frozenset({
    "maccyrillic",
    "windows-1251",
    "iso-8859-5",
})

# Map ISO encodings to their Windows equivalents
ISO_WIN_MAP = {
    "iso-8859-1": "Windows-1252",
    "iso-8859-2": "Windows-1250",
    "iso-8859-5": "Windows-1251",
    "iso-8859-6": "Windows-1256",
    "iso-8859-7": "Windows-1253",
    "iso-8859-8": "Windows-1255",
    "iso-8859-9": "Windows-1254",
    "iso-8859-13": "Windows-1257",
}


class SBCSGroupProber(CharSetGroupProber):
    def __init__(
        self,
        lang_filter: LanguageFilter = LanguageFilter.ALL,
        encoding_era: EncodingEra = EncodingEra.MODERN_WEB,
    ) -> None:
        super().__init__(lang_filter=lang_filter, encoding_era=encoding_era)

        # Initialize byte pattern tracking for disambiguation heuristics
        self._has_win_bytes = False
        self._has_mac_latin_letter_pattern = False
        self._has_mac_cyrillic_letter_pattern = False
        self._has_euro_sign = False

        hebrew_prober = HebrewProber()
        logical_hebrew_prober = SingleByteCharSetProber(
            WINDOWS_1255_HEBREW_MODEL, is_reversed=False, name_prober=hebrew_prober
        )
        visual_hebrew_prober = SingleByteCharSetProber(
            ISO_8859_8_HEBREW_MODEL, is_reversed=True, name_prober=hebrew_prober
        )
        hebrew_prober.set_model_probers(logical_hebrew_prober, visual_hebrew_prober)

        # TODO: ORDER MATTERS HERE. I changed the order vs what was in master
        #       and several tests failed that did not before. Some thought
        #       should be put into the ordering, and we should consider making
        #       order not matter here, because that is very counter-intuitive.
        self.probers = [
            SingleByteCharSetProber(CP720_ARABIC_MODEL),
            SingleByteCharSetProber(CP864_ARABIC_MODEL),
            SingleByteCharSetProber(ISO_8859_6_ARABIC_MODEL),
            SingleByteCharSetProber(WINDOWS_1256_ARABIC_MODEL),
            SingleByteCharSetProber(CP866_BELARUSIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_5_BELARUSIAN_MODEL),
            SingleByteCharSetProber(MACCYRILLIC_BELARUSIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1251_BELARUSIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_14_BRETON_MODEL),
            SingleByteCharSetProber(CP037_BRETON_MODEL),
            SingleByteCharSetProber(CP500_BRETON_MODEL),
            SingleByteCharSetProber(CP855_BULGARIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_5_BULGARIAN_MODEL),
            SingleByteCharSetProber(MACCYRILLIC_BULGARIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1251_BULGARIAN_MODEL),
            SingleByteCharSetProber(CP852_CROATIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_16_CROATIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_2_CROATIAN_MODEL),
            SingleByteCharSetProber(MACLATIN2_CROATIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1250_CROATIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_2_CZECH_MODEL),
            SingleByteCharSetProber(WINDOWS_1250_CZECH_MODEL),
            SingleByteCharSetProber(CP037_DANISH_MODEL),
            SingleByteCharSetProber(CP500_DANISH_MODEL),
            SingleByteCharSetProber(CP850_DANISH_MODEL),
            SingleByteCharSetProber(CP858_DANISH_MODEL),
            SingleByteCharSetProber(CP865_DANISH_MODEL),
            SingleByteCharSetProber(ISO_8859_15_DANISH_MODEL),
            SingleByteCharSetProber(ISO_8859_1_DANISH_MODEL),
            SingleByteCharSetProber(MACROMAN_DANISH_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_DANISH_MODEL),
            SingleByteCharSetProber(CP037_DUTCH_MODEL),
            SingleByteCharSetProber(CP500_DUTCH_MODEL),
            SingleByteCharSetProber(CP850_DUTCH_MODEL),
            SingleByteCharSetProber(CP858_DUTCH_MODEL),
            SingleByteCharSetProber(ISO_8859_15_DUTCH_MODEL),
            SingleByteCharSetProber(ISO_8859_1_DUTCH_MODEL),
            SingleByteCharSetProber(MACROMAN_DUTCH_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_DUTCH_MODEL),
            SingleByteCharSetProber(CP037_ENGLISH_MODEL),
            SingleByteCharSetProber(CP437_ENGLISH_MODEL),
            SingleByteCharSetProber(CP500_ENGLISH_MODEL),
            SingleByteCharSetProber(CP850_ENGLISH_MODEL),
            SingleByteCharSetProber(CP858_ENGLISH_MODEL),
            SingleByteCharSetProber(ISO_8859_15_ENGLISH_MODEL),
            SingleByteCharSetProber(ISO_8859_1_ENGLISH_MODEL),
            SingleByteCharSetProber(MACROMAN_ENGLISH_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_ENGLISH_MODEL),
            SingleByteCharSetProber(ISO_8859_3_ESPERANTO_MODEL),
            SingleByteCharSetProber(CP775_ESTONIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_13_ESTONIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_4_ESTONIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1257_ESTONIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_6_FARSI_MODEL),
            SingleByteCharSetProber(WINDOWS_1256_FARSI_MODEL),
            SingleByteCharSetProber(CP037_FINNISH_MODEL),
            SingleByteCharSetProber(CP500_FINNISH_MODEL),
            SingleByteCharSetProber(CP850_FINNISH_MODEL),
            SingleByteCharSetProber(CP858_FINNISH_MODEL),
            SingleByteCharSetProber(ISO_8859_15_FINNISH_MODEL),
            SingleByteCharSetProber(ISO_8859_1_FINNISH_MODEL),
            SingleByteCharSetProber(MACROMAN_FINNISH_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_FINNISH_MODEL),
            SingleByteCharSetProber(CP037_FRENCH_MODEL),
            SingleByteCharSetProber(CP500_FRENCH_MODEL),
            SingleByteCharSetProber(CP850_FRENCH_MODEL),
            SingleByteCharSetProber(CP858_FRENCH_MODEL),
            SingleByteCharSetProber(CP863_FRENCH_MODEL),
            SingleByteCharSetProber(ISO_8859_15_FRENCH_MODEL),
            SingleByteCharSetProber(ISO_8859_1_FRENCH_MODEL),
            SingleByteCharSetProber(MACROMAN_FRENCH_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_FRENCH_MODEL),
            SingleByteCharSetProber(CP037_GERMAN_MODEL),
            SingleByteCharSetProber(CP500_GERMAN_MODEL),
            SingleByteCharSetProber(CP850_GERMAN_MODEL),
            SingleByteCharSetProber(CP858_GERMAN_MODEL),
            SingleByteCharSetProber(ISO_8859_15_GERMAN_MODEL),
            SingleByteCharSetProber(ISO_8859_1_GERMAN_MODEL),
            SingleByteCharSetProber(MACROMAN_GERMAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_GERMAN_MODEL),
            SingleByteCharSetProber(CP737_GREEK_MODEL),
            SingleByteCharSetProber(CP869_GREEK_MODEL),
            SingleByteCharSetProber(CP875_GREEK_MODEL),
            SingleByteCharSetProber(ISO_8859_7_GREEK_MODEL),
            SingleByteCharSetProber(MACGREEK_GREEK_MODEL),
            SingleByteCharSetProber(WINDOWS_1253_GREEK_MODEL),
            SingleByteCharSetProber(CP424_HEBREW_MODEL, is_reversed=True),
            SingleByteCharSetProber(CP856_HEBREW_MODEL, is_reversed=True),
            SingleByteCharSetProber(CP862_HEBREW_MODEL, is_reversed=True),
            hebrew_prober,
            logical_hebrew_prober,
            visual_hebrew_prober,
            SingleByteCharSetProber(CP852_HUNGARIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_16_HUNGARIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_2_HUNGARIAN_MODEL),
            SingleByteCharSetProber(MACLATIN2_HUNGARIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1250_HUNGARIAN_MODEL),
            SingleByteCharSetProber(CP037_ICELANDIC_MODEL),
            SingleByteCharSetProber(CP500_ICELANDIC_MODEL),
            SingleByteCharSetProber(CP861_ICELANDIC_MODEL),
            SingleByteCharSetProber(ISO_8859_10_ICELANDIC_MODEL),
            SingleByteCharSetProber(ISO_8859_1_ICELANDIC_MODEL),
            SingleByteCharSetProber(MACICELAND_ICELANDIC_MODEL),
            SingleByteCharSetProber(CP037_INDONESIAN_MODEL),
            SingleByteCharSetProber(CP500_INDONESIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_1_INDONESIAN_MODEL),
            SingleByteCharSetProber(MACROMAN_INDONESIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_INDONESIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_14_IRISH_MODEL),
            SingleByteCharSetProber(CP037_IRISH_MODEL),
            SingleByteCharSetProber(CP500_IRISH_MODEL),
            SingleByteCharSetProber(CP037_ITALIAN_MODEL),
            SingleByteCharSetProber(CP500_ITALIAN_MODEL),
            SingleByteCharSetProber(CP850_ITALIAN_MODEL),
            SingleByteCharSetProber(CP858_ITALIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_15_ITALIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_1_ITALIAN_MODEL),
            SingleByteCharSetProber(MACROMAN_ITALIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_ITALIAN_MODEL),
            SingleByteCharSetProber(KZ1048_KAZAKH_MODEL),
            SingleByteCharSetProber(PTCP154_KAZAKH_MODEL),
            SingleByteCharSetProber(CP775_LATVIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_13_LATVIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_4_LATVIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1257_LATVIAN_MODEL),
            SingleByteCharSetProber(CP775_LITHUANIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_13_LITHUANIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_4_LITHUANIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1257_LITHUANIAN_MODEL),
            SingleByteCharSetProber(CP855_MACEDONIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_5_MACEDONIAN_MODEL),
            SingleByteCharSetProber(MACCYRILLIC_MACEDONIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1251_MACEDONIAN_MODEL),
            SingleByteCharSetProber(CP037_MALAY_MODEL),
            SingleByteCharSetProber(CP500_MALAY_MODEL),
            SingleByteCharSetProber(ISO_8859_1_MALAY_MODEL),
            SingleByteCharSetProber(MACROMAN_MALAY_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_MALAY_MODEL),
            SingleByteCharSetProber(ISO_8859_3_MALTESE_MODEL),
            SingleByteCharSetProber(CP037_NORWEGIAN_MODEL),
            SingleByteCharSetProber(CP500_NORWEGIAN_MODEL),
            SingleByteCharSetProber(CP850_NORWEGIAN_MODEL),
            SingleByteCharSetProber(CP858_NORWEGIAN_MODEL),
            SingleByteCharSetProber(CP865_NORWEGIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_15_NORWEGIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_1_NORWEGIAN_MODEL),
            SingleByteCharSetProber(MACROMAN_NORWEGIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_NORWEGIAN_MODEL),
            SingleByteCharSetProber(CP852_POLISH_MODEL),
            SingleByteCharSetProber(ISO_8859_16_POLISH_MODEL),
            SingleByteCharSetProber(ISO_8859_2_POLISH_MODEL),
            SingleByteCharSetProber(MACLATIN2_POLISH_MODEL),
            SingleByteCharSetProber(WINDOWS_1250_POLISH_MODEL),
            SingleByteCharSetProber(CP037_PORTUGUESE_MODEL),
            SingleByteCharSetProber(CP500_PORTUGUESE_MODEL),
            SingleByteCharSetProber(CP850_PORTUGUESE_MODEL),
            SingleByteCharSetProber(CP858_PORTUGUESE_MODEL),
            SingleByteCharSetProber(CP860_PORTUGUESE_MODEL),
            SingleByteCharSetProber(ISO_8859_15_PORTUGUESE_MODEL),
            SingleByteCharSetProber(ISO_8859_1_PORTUGUESE_MODEL),
            SingleByteCharSetProber(MACROMAN_PORTUGUESE_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_PORTUGUESE_MODEL),
            SingleByteCharSetProber(CP852_ROMANIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_16_ROMANIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_2_ROMANIAN_MODEL),
            SingleByteCharSetProber(MACLATIN2_ROMANIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1250_ROMANIAN_MODEL),
            SingleByteCharSetProber(CP855_RUSSIAN_MODEL),
            SingleByteCharSetProber(CP866_RUSSIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_5_RUSSIAN_MODEL),
            SingleByteCharSetProber(KOI8_R_RUSSIAN_MODEL),
            SingleByteCharSetProber(MACCYRILLIC_RUSSIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1251_RUSSIAN_MODEL),
            SingleByteCharSetProber(CP855_SERBIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_5_SERBIAN_MODEL),
            SingleByteCharSetProber(MACCYRILLIC_SERBIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1251_SERBIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_14_SCOTTISH_GAELIC_MODEL),
            SingleByteCharSetProber(CP037_SCOTTISH_GAELIC_MODEL),
            SingleByteCharSetProber(CP500_SCOTTISH_GAELIC_MODEL),
            SingleByteCharSetProber(CP852_SLOVAK_MODEL),
            SingleByteCharSetProber(ISO_8859_16_SLOVAK_MODEL),
            SingleByteCharSetProber(ISO_8859_2_SLOVAK_MODEL),
            SingleByteCharSetProber(MACLATIN2_SLOVAK_MODEL),
            SingleByteCharSetProber(WINDOWS_1250_SLOVAK_MODEL),
            SingleByteCharSetProber(CP852_SLOVENE_MODEL),
            SingleByteCharSetProber(ISO_8859_16_SLOVENE_MODEL),
            SingleByteCharSetProber(ISO_8859_2_SLOVENE_MODEL),
            SingleByteCharSetProber(MACLATIN2_SLOVENE_MODEL),
            SingleByteCharSetProber(WINDOWS_1250_SLOVENE_MODEL),
            SingleByteCharSetProber(CP037_SPANISH_MODEL),
            SingleByteCharSetProber(CP500_SPANISH_MODEL),
            SingleByteCharSetProber(CP850_SPANISH_MODEL),
            SingleByteCharSetProber(CP858_SPANISH_MODEL),
            SingleByteCharSetProber(ISO_8859_15_SPANISH_MODEL),
            SingleByteCharSetProber(ISO_8859_1_SPANISH_MODEL),
            SingleByteCharSetProber(MACROMAN_SPANISH_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_SPANISH_MODEL),
            SingleByteCharSetProber(CP037_SWEDISH_MODEL),
            SingleByteCharSetProber(CP500_SWEDISH_MODEL),
            SingleByteCharSetProber(CP850_SWEDISH_MODEL),
            SingleByteCharSetProber(CP858_SWEDISH_MODEL),
            SingleByteCharSetProber(ISO_8859_15_SWEDISH_MODEL),
            SingleByteCharSetProber(ISO_8859_1_SWEDISH_MODEL),
            SingleByteCharSetProber(MACROMAN_SWEDISH_MODEL),
            SingleByteCharSetProber(WINDOWS_1252_SWEDISH_MODEL),
            SingleByteCharSetProber(KOI8_T_TAJIK_MODEL),
            SingleByteCharSetProber(CP874_THAI_MODEL),
            SingleByteCharSetProber(ISO_8859_11_THAI_MODEL),
            SingleByteCharSetProber(TIS_620_THAI_MODEL),
            SingleByteCharSetProber(CP1026_TURKISH_MODEL),
            SingleByteCharSetProber(CP857_TURKISH_MODEL),
            SingleByteCharSetProber(ISO_8859_3_TURKISH_MODEL),
            SingleByteCharSetProber(ISO_8859_9_TURKISH_MODEL),
            SingleByteCharSetProber(MACTURKISH_TURKISH_MODEL),
            SingleByteCharSetProber(WINDOWS_1254_TURKISH_MODEL),
            SingleByteCharSetProber(CP1125_UKRAINIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_5_UKRAINIAN_MODEL),
            SingleByteCharSetProber(KOI8_U_UKRAINIAN_MODEL),
            SingleByteCharSetProber(MACCYRILLIC_UKRAINIAN_MODEL),
            SingleByteCharSetProber(WINDOWS_1251_UKRAINIAN_MODEL),
            SingleByteCharSetProber(ISO_8859_14_WELSH_MODEL),
            SingleByteCharSetProber(CP037_WELSH_MODEL),
            SingleByteCharSetProber(CP500_WELSH_MODEL),
            SingleByteCharSetProber(WINDOWS_1258_VIETNAMESE_MODEL),
        ]

        # Filter probers based on encoding era and language
        self.probers = self._filter_probers(self.probers)
        self.reset()

    def reset(self) -> None:
        super().reset()
        self._has_win_bytes = False
        self._has_mac_latin_letter_pattern = False
        self._has_mac_cyrillic_letter_pattern = False
        self._has_euro_sign = False

    def feed(self, byte_str: Union[bytes, bytearray]) -> "ProbingState":
        # Detect byte patterns (only check new bytes for efficiency)
        if WIN_BYTE_DETECTOR.search(byte_str):
            self._has_win_bytes = True
        if MAC_LETTER_IN_WORD_DETECTOR.search(
            byte_str
        ) or MAC_LATIN_ONLY_LETTER_DETECTOR.search(byte_str):
            self._has_mac_latin_letter_pattern = True
        if MAC_CYRILLIC_ONLY_LETTER_DETECTOR.search(byte_str):
            self._has_mac_cyrillic_letter_pattern = True
        if EURO_SIGN_DETECTOR.search(byte_str):
            self._has_euro_sign = True

        # Call parent feed method
        return super().feed(byte_str)

    def get_confidence(self) -> float:
        # Get base confidence from parent
        base_confidence = super().get_confidence()

        # If no best prober yet, return base confidence
        if not self._best_guess_prober:
            return base_confidence

        # Apply heuristics to disambiguate confused encodings
        charset_name = self._best_guess_prober.charset_name
        if not charset_name:
            return base_confidence

        confidence = base_confidence
        lower_charset_name = charset_name.lower()

        # Build alternatives dict: best prober for each charset (excluding winner)
        alternatives = {}
        for prober in self.probers:
            if not prober.active or prober == self._best_guess_prober:
                continue
            alt_name = (prober.charset_name or "").lower()
            alt_conf = prober.get_confidence()
            if alt_name not in alternatives or alt_conf > alternatives[alt_name][1]:
                alternatives[alt_name] = (prober, alt_conf)

        # Heuristic 1: Mac/Windows/ISO disambiguation for LATIN encodings
        is_latin_family = lower_charset_name in CONFUSED_LATIN_ENCODINGS

        if is_latin_family and lower_charset_name == "macroman":
            # MacRoman wins but no Mac patterns → prefer ISO/Windows
            # If we have Win bytes, prefer Windows encodings specifically
            if not self._has_mac_latin_letter_pattern:
                alt_names = (
                    ("windows-1252", "iso-8859-1", "iso-8859-15")
                    if self._has_win_bytes
                    else ("iso-8859-1", "windows-1252", "iso-8859-15")
                )
                for alt_name in alt_names:
                    if alt_name in alternatives:
                        prober, alt_conf = alternatives[alt_name]
                        if alt_conf >= confidence * 0.995:  # Within 0.5%
                            self._best_guess_prober = prober
                            return alt_conf

        # Cross-family Mac vs Windows disambiguation
        # If ANY Mac encoding wins but we have Windows bytes and no Mac patterns,
        # prefer any close Windows alternative (even from different language family)
        # This handles cases where MacRoman/MacLatin2/etc wins against text in a different family
        if (
            lower_charset_name.startswith("mac")
            and self._has_win_bytes
            and not self._has_mac_latin_letter_pattern
        ):
            # Look for Windows alternatives
            win_alternatives = [
                (name, prober, conf)
                for name, (prober, conf) in alternatives.items()
                if name.startswith("windows-")
            ]
            if win_alternatives:
                # Sort by confidence and take the best Windows alternative
                win_alternatives.sort(key=lambda x: -x[2])
                best_win_name, best_win_prober, best_win_conf = win_alternatives[0]
                if best_win_conf >= confidence * 0.995:  # Within 0.5%
                    self._best_guess_prober = best_win_prober
                    return best_win_conf

        elif lower_charset_name.startswith("iso-8859"):
            is_latin_iso = lower_charset_name in CONFUSED_LATIN_ENCODINGS

            # ISO wins and has Windows bytes → switch to Windows
            if self._has_win_bytes:
                should_switch = True
                # But check if Mac is close with Mac patterns (Latin only)
                if is_latin_iso and self._has_mac_latin_letter_pattern:
                    for mac_name in alternatives:
                        if (
                            mac_name.startswith("mac")
                            and mac_name in CONFUSED_LATIN_ENCODINGS
                        ):
                            _, mac_conf = alternatives[mac_name]
                            if mac_conf >= confidence * 0.995:
                                should_switch = False
                                break

                if should_switch:
                    win_name = ISO_WIN_MAP.get(lower_charset_name)
                    if win_name and win_name.lower() in alternatives:
                        prober, alt_conf = alternatives[win_name.lower()]
                        self._best_guess_prober = prober
                        return alt_conf

            # ISO-8859-1 with Euro sign → prefer ISO-8859-15
            if lower_charset_name == "iso-8859-1" and self._has_euro_sign:
                if "iso-8859-15" in alternatives:
                    prober, alt_conf = alternatives["iso-8859-15"]
                    if alt_conf >= confidence * 0.99:
                        self._best_guess_prober = prober
                        return alt_conf

        # Heuristic 2: Euro sign detection for Latin encodings
        if self._has_euro_sign and "iso-8859-15" in alternatives:
            is_latin_encoding = lower_charset_name in CONFUSED_LATIN_ENCODINGS
            if is_latin_encoding:
                prober, alt_conf = alternatives["iso-8859-15"]
                if alt_conf >= confidence * 0.99:
                    self._best_guess_prober = prober
                    return alt_conf

        # Heuristic 3: Prefer Mac over Windows/ISO when Mac Latin letter patterns present
        if self._has_mac_latin_letter_pattern:
            mac_alternatives = [
                name
                for name in alternatives
                if name.startswith("mac") and name in CONFUSED_LATIN_ENCODINGS
            ]
            for mac_name in mac_alternatives:
                prober, mac_conf = alternatives[mac_name]
                is_latin_win_or_iso = (
                    lower_charset_name in CONFUSED_LATIN_ENCODINGS
                    and not lower_charset_name.startswith("mac")
                )
                if is_latin_win_or_iso and mac_conf >= confidence * 0.90:
                    self._best_guess_prober = prober
                    return mac_conf

        # Heuristic 4: Mac/Windows/ISO disambiguation for CYRILLIC encodings
        is_cyrillic_family = lower_charset_name in CONFUSED_CYRILLIC_ENCODINGS

        if is_cyrillic_family and lower_charset_name == "maccyrillic":
            # MacCyrillic wins but no Mac Cyrillic patterns → prefer Windows/ISO
            if not self._has_mac_cyrillic_letter_pattern and not self._has_win_bytes:
                for alt_name in ("windows-1251", "iso-8859-5"):
                    if alt_name in alternatives:
                        prober, alt_conf = alternatives[alt_name]
                        if alt_conf >= confidence * 0.995:
                            self._best_guess_prober = prober
                            return alt_conf

        elif is_cyrillic_family and lower_charset_name == "iso-8859-5":
            # ISO-8859-5 wins and has Windows bytes → switch to Windows-1251
            if self._has_win_bytes:
                should_switch = True
                if (
                    self._has_mac_cyrillic_letter_pattern
                    and "maccyrillic" in alternatives
                ):
                    _, mac_conf = alternatives["maccyrillic"]
                    if mac_conf >= confidence * 0.995:
                        should_switch = False

                if should_switch and "windows-1251" in alternatives:
                    prober, alt_conf = alternatives["windows-1251"]
                    self._best_guess_prober = prober
                    return alt_conf

        # Heuristic 5: Prefer MacCyrillic when Mac Cyrillic letter patterns present
        if self._has_mac_cyrillic_letter_pattern and "maccyrillic" in alternatives:
            prober, mac_conf = alternatives["maccyrillic"]
            is_cyrillic_win_or_iso = (
                lower_charset_name in CONFUSED_CYRILLIC_ENCODINGS
                and lower_charset_name != "maccyrillic"
            )
            if is_cyrillic_win_or_iso and mac_conf >= confidence * 0.90:
                self._best_guess_prober = prober
                return mac_conf

        # Heuristic 6: Mac/Windows/ISO disambiguation for CENTRAL EUROPEAN encodings
        is_central_european_family = (
            lower_charset_name in CONFUSED_CENTRAL_EUROPEAN_ENCODINGS
        )

        if is_central_european_family and lower_charset_name == "maclatin2":
            # MacLatin2 wins but no Mac patterns → prefer Windows/ISO
            if not self._has_mac_latin_letter_pattern:
                alt_names = (
                    ("windows-1250", "iso-8859-2")
                    if self._has_win_bytes
                    else ("iso-8859-2", "windows-1250")
                )
                for alt_name in alt_names:
                    if alt_name in alternatives:
                        prober, alt_conf = alternatives[alt_name]
                        if alt_conf >= confidence * 0.995:
                            self._best_guess_prober = prober
                            return alt_conf

        elif is_central_european_family and lower_charset_name == "iso-8859-2":
            # ISO-8859-2 wins and has Windows bytes → switch to Windows-1250
            if self._has_win_bytes:
                should_switch = True
                if self._has_mac_latin_letter_pattern and "maclatin2" in alternatives:
                    _, mac_conf = alternatives["maclatin2"]
                    if mac_conf >= confidence * 0.995:
                        should_switch = False

                if should_switch and "windows-1250" in alternatives:
                    prober, alt_conf = alternatives["windows-1250"]
                    self._best_guess_prober = prober
                    return alt_conf

        # Heuristic 7: Prefer MacLatin2 when Mac Latin letter patterns present
        if self._has_mac_latin_letter_pattern and "maclatin2" in alternatives:
            prober, mac_conf = alternatives["maclatin2"]
            is_central_european_win_or_iso = (
                lower_charset_name in CONFUSED_CENTRAL_EUROPEAN_ENCODINGS
                and lower_charset_name != "maclatin2"
            )
            if is_central_european_win_or_iso and mac_conf >= confidence * 0.90:
                self._best_guess_prober = prober
                return mac_conf

        return confidence
