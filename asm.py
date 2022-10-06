import sys
from typing import List

import instructions


def remove_comments(lines: List[str]) -> List[str]:
    return list(filter(lambda line: not line.startswith('#'), lines))


def remove_empty(lines: List[str]) -> List[str]:
    return list(filter(lambda line: line != '', lines))


def read_file(filepath: str) -> List[str]:
    with open(filepath, 'r') as file:
        lines = [line.strip() for line in file]
    lines = remove_comments(lines)
    lines = remove_empty(lines)
    return lines


def write_file(filepath: str, lines: List[str]) -> None:
    with open(filepath, 'w') as file:
        for line in lines:
            file.write(f"{line}\n")


def assemble_file(filepath: str) -> None:
    lines = read_file(filepath)
    write_file('out.txt', lines)


if __name__ == '__main__':
    assembly_filepath = sys.argv[1]
    assemble_file(assembly_filepath)
