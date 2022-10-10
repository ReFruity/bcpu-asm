from unittest import TestCase

from asm import parse_asm_lines, prefix_negative_relative_branch, prefix_positive_relative_branch, high_four_bits, \
    low_four_bits, \
    fill_addresses, fill_relative_immediates, prefix_non_relative_branch, \
    fill_absolute_immediates, fill_data_immediates


def assert_prefix_positive_relative_branch(input_lines, expected_lines):
    asm_lines = parse_asm_lines(input_lines)
    actual = prefix_positive_relative_branch(asm_lines)
    expected = parse_asm_lines(expected_lines)

    assert actual == expected


class Test(TestCase):
    def test_prefix_negative_relative_branch(self):
        asm_lines = parse_asm_lines([
            '.start',
            'LDAM 0',
            'BR .start',
        ])

        actual = prefix_negative_relative_branch(asm_lines)

        expected = parse_asm_lines([
            '.start',
            'LDAM 0',
            'PFIX 0',
            'BR .start',
        ])

        assert actual == expected

    def test_prefix_positive_relative_branch_long(self):
        input_lines = [
            '.start',
            'BR .middle',
            'BR .end',
            *['DATA 0'] * 14,
            '.middle',
            'LDAM 0',
            'DATA 0',
            '.end',
            'LDAM 0',
        ]

        expected_lines = [
            'PFIX 0',
            '.start',
            'BR .middle',
            'PFIX 0',
            'BR .end',
            *['DATA 0'] * 14,
            '.middle',
            'LDAM 0',
            'DATA 0',
            '.end',
            'LDAM 0',
        ]

        assert_prefix_positive_relative_branch(input_lines, expected_lines)

    def test_prefix_positive_relative_branch_short(self):
        input_lines = [
            '.start',
            'BR .middle',
            'BR .end',
            *['DATA 0'] * 14,
            '.middle',
            'LDAM 0',
            '.end',
            'LDAM 0',
        ]

        expected_lines = [
            '.start',
            'BR .middle',
            'BR .end',
            *['DATA 0'] * 14,
            '.middle',
            'LDAM 0',
            '.end',
            'LDAM 0',
        ]

        assert_prefix_positive_relative_branch(input_lines, expected_lines)

    def test_prefix_non_relative_branch(self):
        input_lines = [
            'LDAM .data',
            *['DATA 0'] * 16,
            '.data',
            'DATA 1',
        ]

        expected_lines = [
            'PFIX 0',
            'LDAM .data',
            *['DATA 0'] * 16,
            '.data',
            'DATA 1',
        ]

        input_asm_lines = parse_asm_lines(input_lines)
        actual = prefix_non_relative_branch(input_asm_lines)
        expected = parse_asm_lines(expected_lines)

        assert actual == expected

    def test_prefix_non_relative_branch_data(self):
        input_lines = [
            'DATA .data',
            *['DATA 0'] * 16,
            '.data',
            'DATA 1',
        ]

        input_asm_lines = parse_asm_lines(input_lines)
        actual = prefix_non_relative_branch(input_asm_lines)
        expected = parse_asm_lines(input_lines)

        assert actual == expected

    def test_high_four_bits(self):
        assert high_four_bits(0b1110001) == 0b111

    def test_low_four_bits(self):
        assert low_four_bits(0b1110001) == 1

    def test_fill_relative_immediates(self):
        input_lines = [
            'PFIX 0',
            '.start',
            'BR .end',
            *['DATA 0'] * 16,
            'BR .end',
            'DATA 0',
            '.end',
            'PFIX 0',
            'BR .start',
        ]
        asm_lines = parse_asm_lines(input_lines)
        actual = fill_relative_immediates(asm_lines)

        assert actual[0].argument.immediate == 0x1
        assert actual[1].argument.immediate == 0x2
        assert actual[18].argument.immediate == 0x1
        assert actual[20].argument.immediate == 0xE
        assert actual[21].argument.immediate == 0xB

    def test_fill_relative_immediates_short(self):
        input_lines = [
            'BR .end',
            'DATA 0',
            '.end',
            'LDAM 1',
        ]
        asm_lines = parse_asm_lines(input_lines)
        actual = fill_relative_immediates(asm_lines)

        assert actual[0].argument.immediate == 0x1

    def test_fill_addresses(self):
        asm_lines = parse_asm_lines([
            '.start',
            'DATA 1',
            'LDAM 0',
        ])

        actual = fill_addresses(asm_lines)

        assert len(actual) == 2
        assert actual[0].address == 0
        assert actual[1].address == 1

    def test_fill_absolute_immediates_short(self):
        asm_lines = parse_asm_lines([
            '.start',
            'LDAM .start',
        ])

        actual = fill_absolute_immediates(asm_lines)

        assert len(actual) == 1
        assert actual[0].argument.immediate == 0

    def test_fill_absolute_immediates_long(self):
        asm_lines = parse_asm_lines([
            'PFIX 0',
            'LDAM .end',
            *['DATA 0'] * 16,
            '.end',
            'DATA 1',
        ])

        actual = fill_absolute_immediates(asm_lines)

        assert len(actual) == 19
        assert actual[0].argument.immediate == 1
        assert actual[1].argument.immediate == 2

    def test_fill_absolute_immediates_plus(self):
        asm_lines = parse_asm_lines([
            '.start',
            'LDAM .start + 1',
            'DATA 1'
        ])

        actual = fill_absolute_immediates(asm_lines)

        assert actual[0].argument.immediate == 1

    def test_fill_absolute_immediates_minus(self):
        asm_lines = parse_asm_lines([
            'LDAM .start - 1',
            '.start',
            'DATA 1'
        ])

        actual = fill_absolute_immediates(asm_lines)

        assert actual[0].argument.immediate == 0

    def test_fill_data_immediates_short(self):
        asm_lines = parse_asm_lines([
            '.start',
            'DATA .start + 1',
            'DATA 1',
        ])

        actual = fill_data_immediates(asm_lines)

        assert actual[0].argument.immediate == 1

    def test_fill_data_immediates_long(self):
        asm_lines = parse_asm_lines([
            'DATA .end + 1',
            *['DATA 0'] * 16,
            '.end',
            'DATA 1',
            'DATA 2',
        ])

        actual = fill_data_immediates(asm_lines)

        assert actual[0].argument.immediate == 18
