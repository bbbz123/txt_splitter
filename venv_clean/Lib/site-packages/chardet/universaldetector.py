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
"""
Module containing the UniversalDetector detector class, which is the primary
class a user of ``chardet`` should use.

:author: Mark Pilgrim (initial port to Python)
:author: Shy Shalom (original C code)
:author: Dan Blanchard (major refactoring for 3.0)
:author: Ian Cordasco
"""

import codecs
import logging
import re
from typing import Optional, Union

from .charsetgroupprober import CharSetGroupProber
from .charsetprober import CharSetProber
from .enums import EncodingEra, InputState, LanguageFilter, ProbingState
from .escprober import EscCharSetProber
from .mbcsgroupprober import MBCSGroupProber
from .metadata.charsets import get_charset, is_unicode_encoding
from .resultdict import ResultDict
from .sbcsgroupprober import ISO_WIN_MAP, SBCSGroupProber
from .utf1632prober import UTF1632Prober


class UniversalDetector:
    """
    The ``UniversalDetector`` class underlies the ``chardet.detect`` function
    and coordinates all of the different charset probers.

    To get a ``dict`` containing an encoding and its confidence, you can simply
    run:

    .. code::

            u = UniversalDetector()
            u.feed(some_bytes)
            u.close()
            detected = u.result

    """

    MINIMUM_THRESHOLD = 0.20
    HIGH_BYTE_DETECTOR = re.compile(b"[\x80-\xff]")
    ESC_DETECTOR = re.compile(b"(\033|~{)")
    # Threshold for "very close" confidence scores where era preference applies
    VERY_CLOSE_THRESHOLD = 0.005  # 0.5%

    # Map ISO encodings to their Windows equivalents (imported from sbcsgroupprober)
    ISO_WIN_MAP = ISO_WIN_MAP

    # Based on https://encoding.spec.whatwg.org/#names-and-labels
    # Maps legacy encoding names to their modern/superset equivalents.
    # Uses Python's canonical codec names (case-insensitive).
    LEGACY_MAP = {
        "ascii": "Windows-1252",  # ASCII is subset of Windows-1252
        "euc-kr": "CP949",  # EUC-KR extended by CP949 (aka Windows-949)
        "iso-8859-1": "Windows-1252",  # Latin-1 extended by Windows-1252
        "iso-8859-2": "Windows-1250",  # Central European
        "iso-8859-5": "Windows-1251",  # Cyrillic
        "iso-8859-6": "Windows-1256",  # Arabic
        "iso-8859-7": "Windows-1253",  # Greek
        "iso-8859-8": "Windows-1255",  # Hebrew
        "iso-8859-9": "Windows-1254",  # Turkish
        "iso-8859-11": "CP874",  # Thai, extended by CP874 (aka Windows-874)
        "iso-8859-13": "Windows-1257",  # Baltic
        "tis-620": "CP874",  # Thai, equivalent to Windows-874
    }

    def __init__(
        self,
        lang_filter: LanguageFilter = LanguageFilter.ALL,
        should_rename_legacy: bool | None = None,
        encoding_era: EncodingEra = EncodingEra.MODERN_WEB,
        max_bytes: int = 200_000,
    ) -> None:
        self._esc_charset_prober: Optional[EscCharSetProber] = None
        self._utf1632_prober: Optional[UTF1632Prober] = None
        self._charset_probers: list[CharSetProber] = []
        self.result: ResultDict = {
            "encoding": None,
            "confidence": 0.0,
            "language": None,
        }
        self.done = False
        self._got_data = False
        self._input_state = InputState.PURE_ASCII
        self._last_char = b""
        self.lang_filter = lang_filter
        self.logger = logging.getLogger(__name__)
        if should_rename_legacy is None:
            should_rename_legacy = encoding_era == EncodingEra.MODERN_WEB
        self.should_rename_legacy = should_rename_legacy
        self.encoding_era = encoding_era
        self._total_bytes_fed = 0
        self.max_bytes = max_bytes
        self.reset()

    @property
    def input_state(self) -> int:
        return self._input_state

    @property
    def has_win_bytes(self) -> bool:
        """Check if Windows-specific bytes were detected by the SBCS prober."""
        for prober in self._charset_probers:
            if isinstance(prober, SBCSGroupProber):
                return prober._has_win_bytes
        return False

    @property
    def charset_probers(self) -> list[CharSetProber]:
        return self._charset_probers

    @property
    def nested_probers(self) -> list[CharSetProber]:
        """Get a flat list of all nested charset probers."""
        nested = []
        for prober in self._charset_probers:
            if isinstance(prober, CharSetGroupProber):
                nested.extend(getattr(prober, "probers", []))
            else:
                nested.append(prober)
        return nested

    @property
    def active_probers(self) -> list[CharSetProber]:
        """Get a flat list of all active (not falsey and not in NOT_ME state) nested charset probers."""
        return [prober for prober in self.nested_probers if prober and prober.active]

    def _apply_encoding_heuristics(
        self, charset_name: str, confidence: float, winning_prober: CharSetProber
    ) -> tuple[str, float]:
        """
        Apply heuristic adjustments to the winning encoding based on:
        1. Encoding era preferences (prefer newer/Unicode encodings)
        2. Mac/Windows/ISO byte pattern disambiguation

        Collects all close-confidence alternatives in a single pass and picks
        the best one by era preference and Unicode preference.

        Returns: (adjusted_charset_name, adjusted_confidence)
        """
        lower_charset_name = charset_name.lower()
        winner_charset = get_charset(lower_charset_name)
        winner_era = winner_charset.encoding_era.value
        winner_is_unicode = is_unicode_encoding(lower_charset_name)
        min_confidence = confidence * (1 - self.VERY_CLOSE_THRESHOLD)

        # Collect all close-confidence alternatives that would be preferred
        best_alt_name = None
        best_alt_confidence = confidence
        best_alt_era = winner_era
        best_alt_is_unicode = winner_is_unicode

        for prober in self._charset_probers:
            if not prober or not prober.active or prober == winning_prober:
                continue

            alt_charset_name = (prober.charset_name or "").lower()
            if not alt_charset_name:
                continue

            alt_confidence = prober.get_confidence()
            if alt_confidence < min_confidence:
                continue

            alt_charset = get_charset(alt_charset_name)
            alt_era = alt_charset.encoding_era.value
            alt_is_unicode = is_unicode_encoding(alt_charset_name)

            # Check if this alternative is preferred over the current best
            prefer_over_best = False
            if alt_era < best_alt_era:
                prefer_over_best = True
            elif alt_era == best_alt_era and alt_is_unicode and not best_alt_is_unicode:
                prefer_over_best = True

            if prefer_over_best:
                best_alt_name = alt_charset_name
                best_alt_confidence = alt_confidence
                best_alt_era = alt_era
                best_alt_is_unicode = alt_is_unicode

        if best_alt_name is not None:
            self.logger.debug(
                "Era preference: %s (era %s, unicode=%s) preferred over %s",
                best_alt_name,
                best_alt_era,
                best_alt_is_unicode,
                charset_name,
            )
            charset_name = best_alt_name
            confidence = best_alt_confidence

        return charset_name, confidence

    def _get_utf8_prober(self) -> Optional[CharSetProber]:
        """
        Get the UTF-8 prober from the charset probers.
        Returns None if not found.
        """
        for prober in self.nested_probers:
            if prober.charset_name and "utf-8" in prober.charset_name.lower():
                return prober
        return None

    def reset(self) -> None:
        """
        Reset the UniversalDetector and all of its probers back to their
        initial states.  This is called by ``__init__``, so you only need to
        call this directly in between analyses of different documents.
        """
        self.result = {"encoding": None, "confidence": 0.0, "language": None}
        self.done = False
        self._got_data = False
        self._input_state = InputState.PURE_ASCII
        self._last_char = b""
        self._total_bytes_fed = 0
        if self._esc_charset_prober:
            self._esc_charset_prober.reset()
        if self._utf1632_prober:
            self._utf1632_prober.reset()
        for prober in self._charset_probers:
            prober.reset()

    def feed(self, byte_str: Union[bytes, bytearray]) -> None:
        """
        Takes a chunk of a document and feeds it through all of the relevant
        charset probers.

        After calling ``feed``, you can check the value of the ``done``
        attribute to see if you need to continue feeding the
        ``UniversalDetector`` more data, or if it has made a prediction
        (in the ``result`` attribute).

        .. note::
           You should always call ``close`` when you're done feeding in your
           document if ``done`` is not already ``True``.
        """
        if self.done:
            return

        if not byte_str:
            return

        if not isinstance(byte_str, bytearray):
            byte_str = bytearray(byte_str)

        # First check for known BOMs, since these are guaranteed to be correct
        if not self._got_data:
            # If the data starts with BOM, we know it is UTF
            if byte_str.startswith(codecs.BOM_UTF8):
                # EF BB BF  UTF-8 with BOM
                self.result = {
                    "encoding": "UTF-8-SIG",
                    "confidence": 1.0,
                    "language": "",
                }
            elif byte_str.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
                # FF FE 00 00  UTF-32, little-endian BOM
                # 00 00 FE FF  UTF-32, big-endian BOM
                self.result = {"encoding": "UTF-32", "confidence": 1.0, "language": ""}
            elif byte_str.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
                # FF FE  UTF-16, little endian BOM
                # FE FF  UTF-16, big endian BOM
                self.result = {"encoding": "UTF-16", "confidence": 1.0, "language": ""}
            else:
                # Binary file detection - check for excessive null bytes early
                # But UTF-16/32 have null bytes, so check for patterns first

                # Check for no-BOM UTF-16/32 patterns (alternating nulls)
                # UTF-32LE: XX 00 00 00 pattern (every 4th byte is null)
                # UTF-32BE: 00 00 00 XX pattern (first 3 of 4 bytes are null)
                # UTF-16LE: XX 00 pattern (every other byte is null in odd positions)
                # UTF-16BE: 00 XX pattern (every other byte is null in even positions)
                looks_like_utf16_32 = False

                # Use larger sample for better pattern detection
                sample_size = min(len(byte_str), 200)
                if sample_size >= 50:
                    sample = byte_str[:sample_size]

                    # Count nulls in even and odd positions (for UTF-16 detection)
                    even_nulls = sum(
                        1 for i in range(0, sample_size, 2) if sample[i] == 0
                    )
                    odd_nulls = sum(
                        1 for i in range(1, sample_size, 2) if sample[i] == 0
                    )

                    # Check for UTF-32 patterns (more nulls in groups of 4)
                    # For UTF-32LE: positions 1,2,3 of every 4 bytes might be null
                    # For UTF-32BE: positions 0,1,2 of every 4 bytes might be null
                    if sample_size >= 100:
                        mod1_nulls = sum(
                            1 for i in range(1, sample_size, 4) if sample[i] == 0
                        )
                        mod2_nulls = sum(
                            1 for i in range(2, sample_size, 4) if sample[i] == 0
                        )
                        mod3_nulls = sum(
                            1 for i in range(3, sample_size, 4) if sample[i] == 0
                        )

                        # Strong UTF-32 signal: consistent null pattern in 2+ of the 3 positions
                        utf32_nulls = [mod1_nulls, mod2_nulls, mod3_nulls]
                        if sum(n > sample_size // 8 for n in utf32_nulls) >= 2:
                            looks_like_utf16_32 = True

                    # UTF-16 detection: significant nulls in even OR odd positions
                    # Lower threshold: 12% of positions (24 out of 200)
                    utf16_threshold = sample_size // 16
                    if even_nulls > utf16_threshold or odd_nulls > utf16_threshold:
                        looks_like_utf16_32 = True

                if not looks_like_utf16_32:
                    # Sample first 8KB to detect binary files
                    check_size = min(len(byte_str), 8192)
                    null_count = byte_str[:check_size].count(0)

                    if null_count > check_size * 0.1:  # >10% null bytes
                        # Likely a binary file, not text
                        self.result = {
                            "encoding": None,
                            "confidence": 0.0,
                            "language": "",
                        }
                        self.done = True
                        return

            self._got_data = True
            if self.result["encoding"] is not None:
                self.done = True
                return

        # If none of those matched and we've only see ASCII so far, check
        # for high bytes and escape sequences
        if self._input_state == InputState.PURE_ASCII:
            if self.HIGH_BYTE_DETECTOR.search(byte_str):
                self._input_state = InputState.HIGH_BYTE
            elif (
                self._input_state == InputState.PURE_ASCII
                and self.ESC_DETECTOR.search(self._last_char + byte_str)
            ):
                self._input_state = InputState.ESC_ASCII

        self._last_char = byte_str[-1:]

        # Track total bytes processed
        self._total_bytes_fed += len(byte_str)

        # Stop processing after processing enough data
        # Don't set done=True here, let close() finalize the result
        if self._total_bytes_fed > self.max_bytes:
            return

        # next we will look to see if it is appears to be either a UTF-16 or
        # UTF-32 encoding
        if not self._utf1632_prober:
            self._utf1632_prober = UTF1632Prober()

        if self._utf1632_prober.state == ProbingState.DETECTING:
            if self._utf1632_prober.feed(byte_str) == ProbingState.FOUND_IT:
                self.result = {
                    "encoding": self._utf1632_prober.charset_name,
                    "confidence": self._utf1632_prober.get_confidence(),
                    "language": "",
                }
                self.done = True
                return

        # If we've seen escape sequences, use the EscCharSetProber, which
        # uses a simple state machine to check for known escape sequences in
        # HZ and ISO-2022 encodings, since those are the only encodings that
        # use such sequences.
        if self._input_state == InputState.ESC_ASCII:
            if not self._esc_charset_prober:
                self._esc_charset_prober = EscCharSetProber(self.lang_filter)
            if self._esc_charset_prober.feed(byte_str) == ProbingState.FOUND_IT:
                self.result = {
                    "encoding": self._esc_charset_prober.charset_name,
                    "confidence": self._esc_charset_prober.get_confidence(),
                    "language": self._esc_charset_prober.language,
                }
                self.done = True
        # If we've seen high bytes (i.e., those with values greater than 127),
        # we need to do more complicated checks using all our multi-byte and
        # single-byte probers that are left.  The single-byte probers
        # use character bigram distributions to determine the encoding, whereas
        # the multi-byte probers use a combination of character unigram and
        # bigram distributions.
        elif self._input_state == InputState.HIGH_BYTE:
            if not self._charset_probers:
                self._charset_probers = [
                    MBCSGroupProber(
                        lang_filter=self.lang_filter, encoding_era=self.encoding_era
                    )
                ]
                # If we're checking non-CJK encodings, use single-byte prober
                if self.lang_filter & LanguageFilter.NON_CJK:
                    self._charset_probers.append(
                        SBCSGroupProber(
                            encoding_era=self.encoding_era, lang_filter=self.lang_filter
                        )
                    )
            for prober in self._charset_probers:
                if prober.feed(byte_str) == ProbingState.FOUND_IT:
                    charset_name = prober.charset_name
                    # Rename legacy encodings if requested
                    if self.should_rename_legacy:
                        charset_name = self.LEGACY_MAP.get(
                            (charset_name or "").lower(), charset_name
                        )
                    self.result = {
                        "encoding": charset_name,
                        "confidence": prober.get_confidence(),
                        "language": prober.language,
                    }
                    self.done = True
                    break

    def close(self) -> ResultDict:
        """
        Stop analyzing the current document and come up with a final
        prediction.

        :returns:  The ``result`` attribute, a ``dict`` with the keys
                   `encoding`, `confidence`, and `language`.
        """
        # Don't bother with checks if we're already done
        if self.done:
            return self.result
        self.done = True

        if not self._got_data:
            self.logger.debug("no data received!")

        # Default to ASCII if it is all we've seen so far
        elif self._input_state == InputState.PURE_ASCII:
            self.result = {"encoding": "ascii", "confidence": 1.0, "language": ""}

        # Check if escape prober found anything
        elif self._input_state == InputState.ESC_ASCII:
            if self._esc_charset_prober:
                charset_name = self._esc_charset_prober.charset_name
                if charset_name:
                    self.result = {
                        "encoding": charset_name,
                        "confidence": self._esc_charset_prober.get_confidence(),
                        "language": self._esc_charset_prober.language,
                    }
                else:
                    # ESC prober didn't identify a specific encoding
                    # Since input is pure ASCII + ESC, default to UTF-8
                    self.result = {
                        "encoding": "utf-8",
                        "confidence": 1.0,
                        "language": "",
                    }

        # If we have seen non-ASCII, return the best that met MINIMUM_THRESHOLD
        elif self._input_state == InputState.HIGH_BYTE:
            prober_confidence = None
            max_prober_confidence = 0.0
            max_prober = None
            for prober in self._charset_probers:
                if not prober:
                    continue
                prober_confidence = prober.get_confidence()
                if prober_confidence > max_prober_confidence:
                    max_prober_confidence = prober_confidence
                    max_prober = prober
            if max_prober and (max_prober_confidence > self.MINIMUM_THRESHOLD):
                charset_name = max_prober.charset_name
                assert charset_name is not None
                lower_charset_name = charset_name.lower()
                confidence = max_prober.get_confidence()

                # Find the actual winning nested prober (max_prober might be a group prober)
                winning_nested_prober = None
                for prober in self.nested_probers:
                    if (
                        prober
                        and prober.active
                        and prober.charset_name
                        and prober.charset_name.lower() == lower_charset_name
                        and abs(prober.get_confidence() - confidence) < 0.0001
                    ):
                        winning_nested_prober = prober
                        break

                # Apply heuristic adjustments in a single pass over active probers
                charset_name, confidence = self._apply_encoding_heuristics(
                    charset_name, confidence, winning_nested_prober or max_prober
                )
                # Rename legacy encodings with superset encodings if asked
                if self.should_rename_legacy:
                    charset_name = self.LEGACY_MAP.get(
                        (charset_name or "").lower(), charset_name
                    )
                self.result = {
                    "encoding": charset_name,
                    "confidence": confidence,
                    "language": max_prober.language,
                }
            else:
                # Default to UTF-8 if no encoding met threshold AND UTF-8 prober
                # hasn't determined this is NOT UTF-8
                # UTF-8 is now the most common encoding on the web and a superset of ASCII
                utf8_prober = self._get_utf8_prober()
                if utf8_prober and utf8_prober.active:
                    # UTF-8 prober didn't rule it out, so default to UTF-8
                    self.result = {
                        "encoding": utf8_prober.charset_name,
                        "confidence": utf8_prober.get_confidence(),
                        "language": utf8_prober.language,
                    }
                else:
                    # UTF-8 was ruled out, return None
                    self.result = {
                        "encoding": None,
                        "confidence": 0.0,
                        "language": None,
                    }

        # Log all prober confidences if none met MINIMUM_THRESHOLD
        if self.logger.getEffectiveLevel() <= logging.DEBUG:
            if self.result["encoding"] is None:
                self.logger.debug("no probers hit minimum threshold")
                for prober in self.nested_probers:
                    if not prober:
                        continue
                    self.logger.debug(
                        "%s %s confidence = %s",
                        prober.charset_name,
                        prober.language,
                        prober.get_confidence(),
                    )
        return self.result
