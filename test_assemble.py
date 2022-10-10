from unittest import TestCase

from asm import read_file_lines, assemble, to_hex, group_code


def assert_programme(programme_name):
    asm_code = read_file_lines(f'programmes/{programme_name}.s')
    machine_code = assemble(asm_code)
    hex_code = to_hex(machine_code)
    groupped_code = group_code(hex_code)
    actual_code = '\n'.join(groupped_code) + '\n'
    expected_code = open(f'programmes/{programme_name}.txt').read()

    assert actual_code == expected_code


class Test(TestCase):
    def test_insertion_sort(self):
        assert_programme('insertion_sort')

    def test_multiplication(self):
        assert_programme('multiplication')
