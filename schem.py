import mcschematic

from util import is_bit_set

BARREL_15 = 'minecraft:barrel{Items: [{Slot: 0b, id: "minecraft:redstone", Count: 64b}, {Count: 64b, Slot: 1b, id: "minecraft:redstone"}, {Slot: 2b, Count: 64b, id: "minecraft:redstone"}, {id: "minecraft:redstone", Slot: 3b, Count: 64b}, {Count: 64b, Slot: 4b, id: "minecraft:redstone"}, {Count: 64b, Slot: 5b, id: "minecraft:redstone"}, {id: "minecraft:redstone", Slot: 6b, Count: 64b}, {id: "minecraft:redstone", Slot: 7b, Count: 64b}, {Count: 64b, id: "minecraft:redstone", Slot: 8b}, {id: "minecraft:redstone", Slot: 9b, Count: 64b}, {Slot: 10b, Count: 64b, id: "minecraft:redstone"}, {id: "minecraft:redstone", Slot: 11b, Count: 64b}, {Slot: 12b, Count: 64b, id: "minecraft:redstone"}, {Count: 64b, Slot: 13b, id: "minecraft:redstone"}, {id: "minecraft:redstone", Count: 64b, Slot: 14b}, {id: "minecraft:redstone", Slot: 15b, Count: 64b}, {id: "minecraft:redstone", Count: 64b, Slot: 16b}, {Count: 64b, id: "minecraft:redstone", Slot: 17b}, {Slot: 18b, id: "minecraft:redstone", Count: 64b}, {id: "minecraft:redstone", Count: 64b, Slot: 19b}, {Count: 64b, id: "minecraft:redstone", Slot: 20b}, {Count: 64b, id: "minecraft:redstone", Slot: 21b}, {id: "minecraft:redstone", Slot: 22b, Count: 64b}, {Count: 64b, id: "minecraft:redstone", Slot: 23b}, {id: "minecraft:redstone", Slot: 24b, Count: 64b}, {Count: 64b, id: "minecraft:redstone", Slot: 25b}, {Slot: 26b, Count: 64b, id: "minecraft:redstone"}], id: "minecraft:barrel"}'


class BCPURomBuilder:
    rom: mcschematic.MCSchematic

    def __init__(self):
        self.rom = mcschematic.MCSchematic('template/rom.schem')

    def save(self, filename: str) -> None:
        self.rom.save('schems', filename, mcschematic.Version.JE_1_18_2)

    def write_byte(self, byte: int, address: int) -> None:
        if address > 31:
            raise Exception(f'Byte address is {address} but only 0-31 byte addresses are supported')

        z = -7

        if address > 0xF:
            z = -1

        x = (address & 0b1111) * 2
        y_offset = address % 2

        for i in range(8):
            if is_bit_set(byte, i):
                y = (i * 2 - 14) + y_offset
                self.rom.setBlock((x, y, z), BARREL_15)

    def inspect(self):
        for x in range(31):
            for y in reversed(range(-15, 2)):
                z = -7
                block_data = self.rom.getBlockDataAt((x, y, z))
                print(x, y, z, block_data)

        for x in reversed(range(31)):
            for y in range(-15, 2):
                z = -1
                block_data = self.rom.getBlockDataAt((x, y, z))
                print(x, y, z, block_data)


def generate_schem(filepath: str):
    file_handle = open(filepath, 'r')
    file = file_handle.read()
    bytes_str = file.strip().replace('\n', ' ').split(' ')
    bytes_int = list(map(lambda x: int(x, 16), bytes_str))
    builder = BCPURomBuilder()

    for i in range(len(bytes_int)):
        builder.write_byte(bytes_int[i], i)

    builder.save('modified')


if __name__ == '__main__':
    generate_schem('schems/input.txt')
