from asm_line import parse_argument, Argument


def test_parse_argument_empty():
    assert parse_argument('ADD') is None


def test_parse_argument_value():
    assert parse_argument('LDAM 12') == Argument.from_value(12)


def test_parse_argument_label():
    assert parse_argument('BR .label') == Argument.from_label('.label')