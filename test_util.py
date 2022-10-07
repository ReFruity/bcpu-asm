from unittest import TestCase

from util import split_list


class Test(TestCase):
    def test_split_list(self):
        assert split_list([1, 2, 3, 4, 5], 3) == [[1, 2, 3], [4, 5]]
