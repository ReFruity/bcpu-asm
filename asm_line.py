from typing import Optional, List

import instructions


class Argument:
    label: str = None
    immediate: int = None
    offset: int = None

    @classmethod
    def from_label(cls, label: str, offset: int = 0):
        argument = Argument()
        argument.label = label
        argument.offset = offset
        return argument

    @classmethod
    def from_immediate(cls, immediate: int):
        argument = Argument()
        argument.immediate = immediate
        return argument

    def is_label(self) -> bool:
        return self.label is not None

    def __repr__(self) -> str:
        if self.is_label():
            suffix = ''
            if self.offset != 0:
                sign = '+' if self.offset > 0 else '-'
                suffix = f'{sign}{self.offset}'
            return f'{self.label}{suffix}'
        else:
            return str(self.immediate)

    def __eq__(self, other):
        return self.label == other.label and self.immediate == other.immediate and self.offset == other.offset


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

    def to_int(self) -> int:
        if self.is_data:
            return self.argument.immediate
        else:
            opcode = instructions.MNEMONICS.index(self.mnemonic)
            argument = 0 if self.argument is None else self.argument.immediate
            instruction = (opcode << 4) + argument
            return instruction


def asm_lines_to_machine_code(asm_lines: List[AsmLine]) -> List[int]:
    return [asm_line.to_int() for asm_line in asm_lines]
