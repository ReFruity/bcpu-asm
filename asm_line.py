from typing import Optional

import instructions


class Argument:
    label: str = None
    value: int = None

    @classmethod
    def from_label(cls, label: str):
        argument = Argument()
        argument.label = label
        return argument

    @classmethod
    def from_value(cls, value: int):
        argument = Argument()
        argument.value = value
        return argument

    def is_label(self) -> bool:
        return self.label is not None

    def __repr__(self) -> str:
        return self.label if self.is_label() else str(self.value)

    def __eq__(self, other):
        return self.label == other.label and self.value == other.value


class AsmLine:
    data: int = None
    mnemonic: str = None
    argument: Argument = None
    address: int = None
    label: str = None

    def is_data(self) -> bool:
        return self.data is not None

    def is_relative_branch(self) -> bool:
        return self.mnemonic in ['BR', 'BRZ', 'BRN']

    @classmethod
    def from_instruction(cls, mnemonic: str, argument: Argument):
        asm_line = AsmLine()
        asm_line.mnemonic = mnemonic
        asm_line.argument = argument
        return asm_line

    @classmethod
    def from_data(cls, data: int):
        asm_line = AsmLine()
        asm_line.data = data
        return asm_line

    def __repr__(self) -> str:
        prefix = ''

        if self.label is not None:
            prefix = f'{self.label} '

        if self.is_data():
            asm_line_str = f'DATA {self.data}'
        else:
            asm_line_str = f'{self.mnemonic} {self.argument}'

        return f'{prefix}{asm_line_str}'

    def __eq__(self, other):
        return self.data == other.data and \
               self.mnemonic == other.mnemonic and \
               self.argument == other.argument and \
               self.address == other.address and \
               self.label == other.label


def parse_argument(instruction: str) -> Optional[Argument]:
    split_instruction = instruction.split(' ')

    if len(split_instruction) > 1:
        argument = split_instruction[1]
        if is_label(argument):
            return Argument.from_label(argument)
        else:
            return Argument.from_value(int(argument))
    else:
        return None


def is_label(line: str) -> bool:
    return line.startswith('.')


def is_data(line: str) -> bool:
    return line.startswith('DATA')


def is_instruction(line: str) -> bool:
    return line.split(' ')[0] in instructions.MNEMONICS
