from typing import Optional, List

import instructions


class Argument:
    label: str = None
    immediate: int = None

    @classmethod
    def from_label(cls, label: str):
        argument = Argument()
        argument.label = label
        return argument

    @classmethod
    def from_immediate(cls, immediate: int):
        argument = Argument()
        argument.immediate = immediate
        return argument

    def is_label(self) -> bool:
        return self.label is not None

    def __repr__(self) -> str:
        return self.label if self.is_label() else str(self.immediate)

    def __eq__(self, other):
        return self.label == other.label and self.immediate == other.immediate


class AsmLine:
    is_data: bool = False
    mnemonic: str = None
    argument: Argument = None
    address: int = None
    label: str = None

    def is_relative_branch(self) -> bool:
        return self.mnemonic in ['BR', 'BRZ', 'BRN']

    @classmethod
    def from_instruction(cls, mnemonic: str, argument: Argument):
        asm_line = AsmLine()
        asm_line.mnemonic = mnemonic
        asm_line.argument = argument
        return asm_line

    @classmethod
    def from_data(cls, argument: Argument):
        asm_line = AsmLine()
        asm_line.argument = argument
        asm_line.is_data = True
        return asm_line

    def __repr__(self) -> str:
        prefix = ''

        if self.label is not None:
            prefix = f'{self.label} '

        if self.is_data:
            asm_line_str = f'DATA {self.argument}'
        else:
            asm_line_str = f'{self.mnemonic} {self.argument}'

        return f'{prefix}{asm_line_str}'

    def __eq__(self, other):
        return self.is_data == other.is_data and \
               self.mnemonic == other.mnemonic and \
               self.argument == other.argument and \
               self.address == other.address and \
               self.label == other.label

    def __copy__(self):
        result = Argument()
        result.is_data = self.is_data
        result.mnemonic = self.mnemonic
        result.argument = self.argument
        result.address = self.address
        result.label = self.label

        return result


def parse_argument(instruction: str) -> Optional[Argument]:
    split_instruction = instruction.split(' ')

    if len(split_instruction) > 1:
        argument = split_instruction[1]
        if is_label(argument):
            return Argument.from_label(argument)
        else:
            return Argument.from_immediate(int(argument, 16))
    else:
        return None


def is_label(line: str) -> bool:
    return line.startswith('.')


def is_data(line: str) -> bool:
    return line.startswith('DATA')


def is_instruction(line: str) -> bool:
    return line.split(' ')[0] in instructions.MNEMONICS


def is_alias(line: str) -> bool:
    return line in instructions.ALIASES.keys()


def asm_line_to_int(asm_line: AsmLine) -> int:
    if asm_line.is_data:
        return asm_line.argument.immediate
    else:
        opcode = instructions.MNEMONICS.index(asm_line.mnemonic)
        argument = 0 if asm_line.argument is None else asm_line.argument.immediate
        instruction = (opcode << 4) + argument
        return instruction


def to_machine_code(asm_lines: List[AsmLine]) -> List[int]:
    return [asm_line_to_int(asm_line) for asm_line in asm_lines]