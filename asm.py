import sys
from typing import List

import instructions
from asm_line import AsmLine, is_instruction, parse_argument, is_data, is_label, Argument, to_machine_code


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


def parse_mnemonic(instruction: str) -> str:
    return instruction.split(' ')[0]


def is_relative_branch(mnemonic: str) -> bool:
    return mnemonic in ['BR', 'BRZ', 'BRN']


def parse_data(line: str) -> int:
    return int(line.split(' ')[1])


def parse_asm_lines(lines: List[str]) -> List[AsmLine]:
    result = []
    label = None

    for line in lines:
        if is_instruction(line):
            mnemonic = parse_mnemonic(line)
            argument = parse_argument(line)
            asm_line = AsmLine.from_instruction(mnemonic, argument)
            if label is not None:
                asm_line.label = label
            result.append(asm_line)
            label = None
        elif is_data(line):
            asm_line = AsmLine.from_data(parse_data(line))
            if label is not None:
                asm_line.label = label
            result.append(asm_line)
            label = None
        elif is_label(line):
            label = line
        else:
            raise AssemblyError(f'Unrecognized line {line}')

    return result


def find_label_index(asm_lines: List[AsmLine], label: str) -> int:
    for i in range(len(asm_lines)):
        asm_line = asm_lines[i]
        if asm_line.label == label:
            return i


def prefix_positive_branch(asm_lines: List[AsmLine]) -> List[AsmLine]:
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


def prefix_negative_branch(asm_lines: List[AsmLine]) -> List[AsmLine]:
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


def fill_branch_argument(asm_lines: List[AsmLine]) -> List[AsmLine]:
    max_offset = (1 << 7) - 1
    min_offset = -(1 << 7)
    result = asm_lines.copy()

    i = 1

    while i < len(result):
        asm_line = result[i]

        if asm_line.is_relative_branch() and asm_line.argument.is_label():
            label_index = find_label_index(result, asm_line.argument.label)
            offset = label_index - (i + 1)

            if offset < min_offset:
                raise AssemblyError(f'Relative offset {offset} for line {asm_line} with number {asm_line.address} is less than {min_offset}.')

            if offset > max_offset:
                raise AssemblyError(f'Relative offset {offset} for line {asm_line} with number {asm_line.address} is more than {max_offset}.')

            prefix_arg_immediate = high_four_bits(offset)

            if prefix_arg_immediate != 0:
                prefix_line = result[i - 1]
                if prefix_line.mnemonic != 'PFIX':
                    raise AssemblyError(f'Line {prefix_line} before line {asm_line} with number {asm_line.address} should be PFIX.')
                prefix_arg = Argument.from_immediate(high_four_bits(offset))
                prefix_line.argument = prefix_arg

            branch_arg_immediate = low_four_bits(offset)
            branch_arg = Argument.from_immediate(branch_arg_immediate)
            asm_line.argument = branch_arg

        i += 1

    return result


def fill_addresses(asm_lines: List[AsmLine]) -> List[AsmLine]:
    result = asm_lines.copy()

    for i in range(len(result)):
        asm_line = result[i]
        asm_line.address = i

    return result


def assemble(asm_code: List[str]) -> List[int]:
    lines = remove_comments(asm_code)
    lines = remove_empty(lines)
    asm_lines = parse_asm_lines(lines)
    prefixed_asm_lines = prefix_negative_branch(asm_lines)
    prefixed_asm_lines = prefix_positive_branch(prefixed_asm_lines)
    addressed_asm_lines = fill_addresses(prefixed_asm_lines)
    argumented_asm_lines = fill_branch_argument(addressed_asm_lines)

    return to_machine_code(argumented_asm_lines)


def to_hex(machine_code: List[int]) -> List[str]:
    return [f'{opcode:02x}' for opcode in machine_code]


if __name__ == '__main__':
    asm_filepath = sys.argv[1]
    asm_code = read_file_lines(asm_filepath)
    machine_code = assemble(asm_code)
    write_file('out.txt', to_hex(machine_code))
