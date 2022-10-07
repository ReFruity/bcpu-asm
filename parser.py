from typing import List, Optional

import instructions
from asm_line import Argument, AsmLine


class ParseError(Exception):
    pass


def is_hex(argument: str) -> bool:
    return argument.startswith('0x')


def parse_argument(line: str) -> Optional[Argument]:
    split_line = line.split(' ')

    if len(split_line) == 1:
        return None
    elif len(split_line) == 2:
        argument = split_line[1]
        if is_label(argument):
            return Argument.from_label(argument)
        else:
            if is_hex(argument):
                return Argument.from_immediate(int(argument[2:], 16))
            else:
                return Argument.from_immediate(int(argument, 10))
    elif len(split_line) == 4:
        label = split_line[1]
        if not is_label(label):
            raise ParseError(f'Token {label} is not a valid label.')
        sign = split_line[2]
        operand = int(split_line[3])
        if sign == '+':
            return Argument.from_label(label, operand)
        elif sign == '-':
            return Argument.from_label(label, -operand)
        else:
            raise ParseError(f'Unsupported operation {sign}.')


def is_label(line: str) -> bool:
    return line.startswith('.')


def is_data(line: str) -> bool:
    return line.startswith('DATA')


def is_instruction(line: str) -> bool:
    return line.split(' ')[0] in instructions.MNEMONICS


def is_alias(line: str) -> bool:
    return line in instructions.ALIASES.keys()


def parse_mnemonic(instruction: str) -> str:
    return instruction.split(' ')[0]


def is_relative_branch(mnemonic: str) -> bool:
    return mnemonic in ['BR', 'BRZ', 'BRN']


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
            asm_line = AsmLine.from_data(parse_argument(line))
            if label is not None:
                asm_line.label = label
            result.append(asm_line)
            label = None
        elif is_label(line):
            label = line
        elif is_alias(line):
            alias_lines = instructions.ALIASES[line]
            alias_asm_lines = parse_asm_lines(alias_lines)
            if label is not None:
                alias_asm_lines[0].label = label
            result.extend(alias_asm_lines)
        else:
            raise ParseError(f'Unrecognized line {line}')

    return result