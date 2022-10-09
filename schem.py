import mcschematic


def main():
    schem = mcschematic.MCSchematic('schems/template.schem')
    schem.setBlock((0, 0, 0), 'minecraft:stone')
    print(schem.getBlockDataAt((0, 0, 0)))
    # for i in range(-10, 10):
    #     for j in range(-10, 10):
    #         for k in range(-10, 10):
    #             block_data = schem.getBlockDataAt((i, j, k))
    #             block_state = schem.getBlockStateAt((i, j, k))
    #             print(i, j, k, block_data)
    #             print(i, j, k, block_state)

    # schem.save('schems', 'modified', mcschematic.Version.JE_1_18_2)


if __name__ == '__main__':
    main()
