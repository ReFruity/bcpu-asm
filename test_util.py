from unittest import TestCase

from util import split_list, is_bit_set


class Test(TestCase):
    def test_split_list(self):
        assert split_list([1, 2, 3, 4, 5], 3) == [[1, 2, 3], [4, 5]]

    def test_is_bit_set(self):
        number = 0b10001101

        assert is_bit_set(number, 0) is True
        assert is_bit_set(number, 1) is False
        assert is_bit_set(number, 2) is True
        assert is_bit_set(number, 3) is True
        assert is_bit_set(number, 4) is False
        assert is_bit_set(number, 5) is False
        assert is_bit_set(number, 6) is False
        assert is_bit_set(number, 7) is True

        assert is_bit_set(0, 7) is False