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

import logging
import re
from typing import Optional, Union

from .enums import EncodingEra, LanguageFilter, ProbingState
from .metadata.charsets import Charset, get_charset

INTERNATIONAL_WORDS_PATTERN = re.compile(
    # Pattern rationale (see paper section 4.7 Two-Char Sequence Distribution):
    # We drop words composed solely of ASCII letters for scripts without Latin letters,
    # retaining any word containing at least one high-byte (>=0x80) character.
    # Structure: optional ASCII prefix + one or more high-byte chars + optional ASCII
    # suffix + optional single trailing marker.
    b"[a-zA-Z]*[\x80-\xff]+[a-zA-Z]*[^a-zA-Z\x80-\xff]?"
)


class CharSetProber:
    SHORTCUT_THRESHOLD = 0.95

    def __init__(
        self,
        *,
        lang_filter: LanguageFilter = LanguageFilter.ALL,
        encoding_era: EncodingEra = EncodingEra.ALL,
    ) -> None:
        self._state = ProbingState.DETECTING
        self.active = True
        self.lang_filter = lang_filter
        self.encoding_era = encoding_era
        self.logger = logging.getLogger(__name__)

    def reset(self) -> None:
        self._state = ProbingState.DETECTING

    @property
    def charset_name(self) -> Optional[str]:
        return None

    @property
    def charset(self) -> Optional[Charset]:
        """Return the Charset metadata for this prober's encoding."""
        name = self.charset_name
        if name is None:
            return None
        return get_charset(name)

    @property
    def language(self) -> Optional[str]:
        raise NotImplementedError

    def feed(self, byte_str: Union[bytes, bytearray]) -> ProbingState:
        raise NotImplementedError

    @property
    def state(self) -> ProbingState:
        return self._state

    def get_confidence(self) -> float:
        return 0.0

    @staticmethod
    def filter_high_byte_only(buf: Union[bytes, bytearray]) -> bytes:
        buf = re.sub(b"([\x00-\x7f])+", b" ", buf)
        return buf

    @staticmethod
    def filter_international_words(buf: Union[bytes, bytearray]) -> bytearray:
        """Filter out ASCII-only words for non-Latin scripts.

        Byte classes:
        - alphabet: ASCII letters [a-zA-Z]
        - international: bytes with high bit set [\x80-\xff]
        - marker: everything else [^a-zA-Z\x80-\xff]

        The buffer is treated as a sequence of "words" separated by marker bytes.
        We KEEP only those words that contain at least one high-byte character,
        i.e. match the pattern: optional ASCII prefix + >=1 high-byte + optional
        ASCII suffix, plus at most one trailing marker. Pure ASCII words are
        discarded as noise when the target language model excludes ASCII letters
        ("English words in other-language pages" — paper §4.7 summary).

        Why we retain surrounding ASCII letters instead of stripping them:
        - Preserves real adjacency for bigram modeling around high-byte letters.
        - Avoids creating artificial bigrams between non-adjacent high-byte chars.

        Trailing marker normalization: a single marker at word end is converted
        to a space if it is an ASCII punctuation/control, collapsing runs of
        markers into one delimiter (reduces noise like repeated punctuation or
        HTML artifacts).

        Usage is conditional: callers apply this ONLY when the language model's
        ``keep_ascii_letters`` is False (see ``SingleByteCharSetProber.feed``).
        Latin-script languages skip this and instead use ``remove_xml_tags``.

        This behavior mirrors the original universalchardet / uchardet approach
        and aligns with the training pipeline which excludes ASCII letters for
        non-Latin alphabets.
        """
        filtered = bytearray()

        # This regex expression filters out only words that have at-least one
        # international character. The word may include one marker character at
        # the end.
        words = INTERNATIONAL_WORDS_PATTERN.findall(buf)

        for word in words:
            filtered.extend(word[:-1])

            # If the last character in the word is a marker, replace it with a
            # space as markers shouldn't affect our analysis (they are used
            # similarly across all languages and may thus have similar
            # frequencies).
            last_char = word[-1:]
            if not last_char.isalpha() and last_char < b"\x80":
                last_char = b" "
            filtered.extend(last_char)

        return filtered

    @staticmethod
    def remove_xml_tags(buf: Union[bytes, bytearray]) -> bytearray:
        """
        Returns a copy of ``buf`` that retains only the sequences of English
        alphabet and high byte characters that are not between <> characters.
        This filter can be applied to all scripts which contain both English
        characters and extended ASCII characters, but is currently only used by
        ``Latin1Prober``.
        """
        filtered = bytearray()
        in_tag = False
        prev = 0
        buf_view = memoryview(buf).cast("c")

        for curr, buf_char in enumerate(buf_view):
            # Check if we're coming out of or entering an XML tag

            # https://github.com/python/typeshed/issues/8182
            if buf_char == b">":  # type: ignore[comparison-overlap]
                prev = curr + 1
                in_tag = False
            # https://github.com/python/typeshed/issues/8182
            elif buf_char == b"<":  # type: ignore[comparison-overlap]
                if curr > prev and not in_tag:
                    # Keep everything after last non-extended-ASCII,
                    # non-alphabetic character
                    filtered.extend(buf[prev:curr])
                    # Output a space to delimit stretch we kept
                    filtered.extend(b" ")
                in_tag = True

        # If we're not in a tag...
        if not in_tag:
            # Keep everything after last non-extended-ASCII, non-alphabetic
            # character
            filtered.extend(buf[prev:])

        return filtered
