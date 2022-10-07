from unittest import TestCase

from asm_line import Argument, AsmLine
from parser import parse_argument, parse_asm_lines


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

    def test_parse_asm_lines_instruction_arg(self):
        actual = parse_asm_lines([
            'LDAM 1',
            'LDAM .start',
            'LDAM .start + 1',
        ])

        assert len(actual) == 3
        assert actual[0] == AsmLine.from_instruction('LDAM', Argument.from_immediate(1))
        assert actual[1] == AsmLine.from_instruction('LDAM', Argument.from_label('.start'))
        assert actual[2] == AsmLine.from_instruction('LDAM', Argument.from_label('.start', offset=1))

    def test_parse_asm_lines_data_arg(self):
        actual = parse_asm_lines([
            'DATA 2',
            'DATA 0xF',
            'DATA 0x12',
            'DATA .start',
            'DATA .start + 1',
        ])

        assert len(actual) == 5
        assert actual[0] == AsmLine.from_data(Argument.from_immediate(2))
        assert actual[1] == AsmLine.from_data(Argument.from_immediate(15))
        assert actual[2] == AsmLine.from_data(Argument.from_immediate(18))
        assert actual[3] == AsmLine.from_data(Argument.from_label('.start'))
        assert actual[4] == AsmLine.from_data(Argument.from_label('.start', offset=1))

    def test_parse_asm_lines_labels(self):
        actual = parse_asm_lines([
            '.start',
            'LDAM 1',
            '.end',
            'HALT',
        ])

        assert len(actual) == 3
        expected_asm_line_0 = AsmLine.from_instruction('LDAM', Argument.from_immediate(1))
        expected_asm_line_0.label = '.start'
        assert actual[0] == expected_asm_line_0
        expected_asm_line_1 = AsmLine.from_instruction('PFIX', Argument.from_immediate(15))
        expected_asm_line_1.label = '.end'
        assert actual[1] == expected_asm_line_1
        assert actual[2] == AsmLine.from_instruction('BR', Argument.from_immediate(14))