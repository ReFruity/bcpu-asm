import sys
from typing import List

from asm_line import AsmLine, Argument, asm_lines_to_machine_code
from parser import parse_asm_lines
from util import split_list


class AssemblyError(Exception):
    pass


def remove_comments(lines: List[str]) -> List[str]:
    return list(filter(lambda line: not line.startswith('#'), lines))


def remove_empty(lines: List[str]) -> List[str]:
    return list(filter(lambda line: line != '', lines))


def read_file_lines(filepath: str) -> List[str]:
    with open(filepath, 'r') as file:
        lines = [line.strip() for line in file]
    return lines


def write_file(filepath: str, lines: List[str]) -> None:
    with open(filepath, 'w') as file:
        for line in lines:
            file.write(f"{line}\n")


def find_label_index(asm_lines: List[AsmLine], label: str) -> int:
    for i in range(len(asm_lines)):
        asm_line = asm_lines[i]
        if asm_line.label == label:
            return i


def prefix_non_relative_branch(asm_lines: List[AsmLine]) -> List[AsmLine]:
    result = asm_lines.copy()

    i = 0

    while i < len(result):
        asm_line = result[i]

        if asm_line.is_non_relative_branch() and asm_line.argument.is_label():
            if asm_line.is_prefix():
                raise AssemblyError(f'Unsupported PFIX with label argument at line number {i + 1}.')

            label_index = find_label_index(result, asm_line.argument.label)
            if label_index > 0xF:
                argument = Argument.from_immediate(0)
                pfix = AsmLine.from_instruction('PFIX', argument)
                result.insert(i, pfix)
                i += 1

        i += 1

    return result


def prefix_positive_relative_branch(asm_lines: List[AsmLine]) -> List[AsmLine]:
    result = asm_lines.copy()

    i = len(result) - 1

    while i >= 0:
        asm_line = result[i]

        if asm_line.is_relative_branch() and asm_line.argument.is_label():
            label_index = find_label_index(result, asm_line.argument.label)
            offset = label_index - i
            if offset > 16:
                argument = Argument.from_immediate(0)
                pfix = AsmLine.from_instruction('PFIX', argument)
                result.insert(i, pfix)

        i -= 1

    return result


def prefix_negative_relative_branch(asm_lines: List[AsmLine]) -> List[AsmLine]:
    result = asm_lines.copy()

    i = 0

    while i < len(result):
        asm_line = result[i]

        if asm_line.is_relative_branch() and asm_line.argument.is_label():
            label_index = find_label_index(result, asm_line.argument.label)
            offset = label_index - i
            if offset < 0:
                argument = Argument.from_immediate(0)
                pfix = AsmLine.from_instruction('PFIX', argument)
                result.insert(i, pfix)
                i += 1

        i += 1

    return result


def high_four_bits(offset: int) -> int:
    return (offset >> 4) & 0b1111


def low_four_bits(offset: int) -> int:
    return offset & 0b1111


def fill_addresses(asm_lines: List[AsmLine]) -> List[AsmLine]:
    result = asm_lines.copy()

    for i in range(len(result)):
        asm_line = result[i]
        asm_line.address = i

    return result


def fill_absolute_immediates(asm_lines: List[AsmLine]) -> List[AsmLine]:
    result = asm_lines.copy()

    i = 0

    while i < len(result):
        asm_line = result[i]

        if asm_line.is_non_relative_branch() and asm_line.argument.is_label():
            label_index = find_label_index(result, asm_line.argument.label)
            label_address = label_index + asm_line.argument.offset

            if label_address > 255:
                raise AssemblyError(f'Error in line {i + 1}: {asm_line}. Only 0-255 addresses are supported in 8-bit BCPU architecture.')

            prefix_arg_immediate = high_four_bits(label_address)

            if prefix_arg_immediate != 0:
                prefix_line = result[i - 1]
                if prefix_line.mnemonic != 'PFIX':
                    raise AssemblyError(f'Line {prefix_line} before line {asm_line} with number {asm_line.address + 1} should be PFIX.')
                prefix_arg = Argument.from_immediate(high_four_bits(label_address))
                prefix_line.argument = prefix_arg

            instruction_arg_immediate = low_four_bits(label_address)
            instruction_arg = Argument.from_immediate(instruction_arg_immediate)
            asm_line.argument = instruction_arg

        i += 1

    return result


def fill_relative_immediates(asm_lines: List[AsmLine]) -> List[AsmLine]:
    max_offset = (1 << 7) - 1
    min_offset = -(1 << 7)
    result = asm_lines.copy()

    i = 0

    while i < len(result):
        asm_line = result[i]

        if asm_line.is_relative_branch() and asm_line.argument.is_label():
            label_index = find_label_index(result, asm_line.argument.label)
            offset = label_index - (i + 1)

            if offset < min_offset:
                raise AssemblyError(f'Relative offset {offset} for line {asm_line} with number {asm_line.address + 1} is less than {min_offset}.')

            if offset > max_offset:
                raise AssemblyError(f'Relative offset {offset} for line {asm_line} with number {asm_line.address + 1} is more than {max_offset}.')

            prefix_arg_immediate = high_four_bits(offset)

            if prefix_arg_immediate != 0:
                prefix_line = result[i - 1]
                if prefix_line.mnemonic != 'PFIX':
                    raise AssemblyError(f'Line {prefix_line} before line {asm_line} with number {asm_line.address + 1} should be PFIX.')
                prefix_arg = Argument.from_immediate(high_four_bits(offset))
                prefix_line.argument = prefix_arg

            branch_arg_immediate = low_four_bits(offset)
            branch_arg = Argument.from_immediate(branch_arg_immediate)
            asm_line.argument = branch_arg

        i += 1

    return result


def fill_data_immediates(asm_lines: List[AsmLine]) -> List[AsmLine]:
    result = asm_lines.copy()

    i = 0

    while i < len(result):
        asm_line = result[i]

        if asm_line.is_data and asm_line.argument.is_label():
            label_index = find_label_index(result, asm_line.argument.label)
            label_address = label_index + asm_line.argument.offset

            if label_address > 255:
                raise AssemblyError(f'Error in line {i + 1}: {asm_line}. Only 0-255 addresses are supported in 8-bit BCPU architecture.')

            instruction_arg = Argument.from_immediate(label_address)
            asm_line.argument = instruction_arg

        i += 1

    return result


def assemble(asm_code: List[str]) -> List[int]:
    lines = remove_comments(asm_code)
    lines = remove_empty(lines)
    asm_lines = parse_asm_lines(lines)
    prefixed_asm_lines = prefix_non_relative_branch(asm_lines)
    prefixed_asm_lines = prefix_negative_relative_branch(prefixed_asm_lines)
    prefixed_asm_lines = prefix_positive_relative_branch(prefixed_asm_lines)
    addressed_asm_lines = fill_addresses(prefixed_asm_lines)
    argumented_asm_lines = fill_absolute_immediates(addressed_asm_lines)
    argumented_asm_lines = fill_relative_immediates(argumented_asm_lines)
    argumented_asm_lines = fill_data_immediates(argumented_asm_lines)

    return asm_lines_to_machine_code(argumented_asm_lines)


def to_hex(machine_code: List[int]) -> List[str]:
    return [f'{opcode:02X}' for opcode in machine_code]


def group_code(str_list: List[str], group_size: int = 16) -> List[str]:
    groups = split_list(str_list, group_size)
    return [' '.join(group) for group in groups]


if __name__ == '__main__':
    asm_filepath = sys.argv[1]
    asm_code = read_file_lines(asm_filepath)
    machine_code = assemble(asm_code)
    hex_code = to_hex(machine_code)
    grouped_code = group_code(hex_code)
    write_file('out.txt', grouped_code)
