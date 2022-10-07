from unittest import TestCase

from asm_line import Argument
from parser import parse_argument


class Test(TestCase):
    def test_parse_argument_empty(self):
        assert parse_argument('ADD') is None

    def test_parse_argument_immediate(self):
        assert parse_argument('LDAM 12') == Argument.from_immediate(12)
        assert parse_argument('LDAM 0xE') == Argument.from_immediate(14)
        assert parse_argument('DATA 0x12') == Argument.from_immediate(18)

    def test_parse_argument_label(self):
        assert parse_argument('BR .label') == Argument.from_label('.label')
        assert parse_argument('BR .label + 2') == Argument.from_label('.label', 2)
        assert parse_argument('BR .label - 2') == Argument.from_label('.label', -2)
