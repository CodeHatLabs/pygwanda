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

    def test_gmtime_string(self):
        gmts = gmtime_string()
        assert len(gmts) == 16
        assert gmts[8] == 'T'
        assert gmts[-1] == 'Z'
        gmts = gmtime_string((2076, 7, 4, 5, 0, 0))
        assert len(gmts) == 16
        assert gmts[8] == 'T'
        assert gmts[-1] == 'Z'
        assert gmts[:4] == '2076'
        assert gmts[4:6] == '07'
        assert gmts[6:8] == '04'
        assert gmts[9:11] == '05'
        assert gmts[11:15] == '0000'

    def test_random_unambiguous_string(self):
        self._do_characters_test(UNAMBIGUOUS_LOWER)
        self._do_characters_test(UNAMBIGUOUS_UPPER)
        self._do_characters_test(UNAMBIGUOUS_DIGITS)
        self._do_characters_test(UNAMBIGUOUS_SYMBOLS)
        self._do_characters_test(UNAMBIGUOUS_ALPHA)
        self._do_characters_test(UNAMBIGUOUS_ALHPANUM)
        self._do_characters_test(UNAMBIGUOUS_ASCII)


