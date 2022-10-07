from asm import parse_asm_lines, prefix_negative_branch, prefix_positive_branch


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