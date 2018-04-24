import pytest
from random import randint

from pygwanda.helpers import *


class TestHelpers:
    """
    One big test for the various helper methods and their modes:
    """

    def _do_characters_test(self, characters):
        testlen = randint(100, 1000)
        result = random_unambiguous_string(testlen, characters)
        assert len(result) == testlen
        for ch in result:
            assert ch in characters

    def test_random_unambiguous_string(self):
        self._do_characters_test(UNAMBIGUOUS_LOWER)
        self._do_characters_test(UNAMBIGUOUS_UPPER)
        self._do_characters_test(UNAMBIGUOUS_DIGITS)
        self._do_characters_test(UNAMBIGUOUS_SYMBOLS)
        self._do_characters_test(UNAMBIGUOUS_ALPHA)
        self._do_characters_test(UNAMBIGUOUS_ALHPANUM)
        self._do_characters_test(UNAMBIGUOUS_ASCII)


