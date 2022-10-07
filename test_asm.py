from asm import parse_asm_lines, prefix_negative_branch, prefix_positive_branch, high_four_bits, low_four_bits, \
    fill_addresses, fill_branch_argument, fill_immediates
from asm_line import Argument, AsmLine


def test_parse_asm_lines_instruction_arg():
    actual = parse_asm_lines([
        'LDAM 1',
        'LDAM .start',
        'LDAM .start + 1',
    ])

    assert len(actual) == 3
    assert actual[0] == AsmLine.from_instruction('LDAM', Argument.from_immediate(1))
    assert actual[1] == AsmLine.from_instruction('LDAM', Argument.from_label('.start'))
    assert actual[2] == AsmLine.from_instruction('LDAM', Argument.from_label('.start + 1'))


def test_parse_asm_lines_data_arg():
    actual = parse_asm_lines([
        'DATA 2',
        'DATA F',
        'DATA 12',
        'DATA .start',
        'DATA .start + 1',
    ])

    assert len(actual) == 5
    assert actual[0] == AsmLine.from_data(Argument.from_immediate(1))
    assert actual[1] == AsmLine.from_data(Argument.from_immediate(15))
    assert actual[2] == AsmLine.from_data(Argument.from_immediate(18))
    assert actual[3] == AsmLine.from_data(Argument.from_label('.start'))
    assert actual[4] == AsmLine.from_data(Argument.from_label('.start + 1'))


def test_parse_asm_lines_labels():
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


def test_prefix_negative_branch():
    asm_lines = parse_asm_lines([
        '.start',
        'LDAM 0',
        'BR .start',
    ])

    actual = prefix_negative_branch(asm_lines)

    expected = parse_asm_lines([
        '.start',
        'LDAM 0',
        'PFIX 0',
        'BR .start',
    ])

    assert expected == actual


def assert_prefix_positive_branch(input_lines, expected_lines):
    asm_lines = parse_asm_lines(input_lines)
    actual = prefix_positive_branch(asm_lines)
    expected = parse_asm_lines(expected_lines)

    assert expected == actual


def test_prefix_positive_branch_long():
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

    assert_prefix_positive_branch(input_lines, expected_lines)


def test_prefix_positive_branch_short():
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

    assert_prefix_positive_branch(input_lines, expected_lines)


def test_high_four_bits():
    assert high_four_bits(0b1110001) == 0b111


def test_low_four_bits():
    assert low_four_bits(0b1110001) == 1


def test_fill_branch_argument():
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
    actual = fill_branch_argument(asm_lines)

    assert actual[0].argument.immediate == 0x1
    assert actual[1].argument.immediate == 0x2
    assert actual[18].argument.immediate == 0x1
    assert actual[20].argument.immediate == 0xE
    assert actual[21].argument.immediate == 0xB


def test_fill_branch_argument_short():
    input_lines = [
        'BR .end',
        'DATA 0',
        '.end',
        'LDAM 1',
    ]
    asm_lines = parse_asm_lines(input_lines)
    actual = fill_branch_argument(asm_lines)

    assert actual[0].argument.immediate == 0x1


def test_fill_addresses():
    asm_lines = parse_asm_lines([
        '.start',
        'DATA 1',
        'LDAM 0',
    ])

    actual = fill_addresses(asm_lines)

    assert len(actual) == 2
    assert actual[0].address == 0
    assert actual[1].address == 1


def test_fill_immediates():
    asm_lines = parse_asm_lines([
        '.start',
        'LDAM .start',
    ])

    actual = fill_immediates(asm_lines)

    assert len(actual) == 1
    assert actual[0].argument.immediate == 0


def test_fill_immediates_plus():
    asm_lines = parse_asm_lines([
        '.start',
        'LDAM .start + 1',
        'DATA 1'
    ])

    actual = fill_immediates(asm_lines)

    assert actual[0].argument.immediate == 1


def test_fill_immediates_minus():
    asm_lines = parse_asm_lines([
        'LDAM .start - 1',
        '.start',
        'DATA 1'
    ])

    actual = fill_immediates(asm_lines)

    assert actual[0].argument.immediate == 0
