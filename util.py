from typing import List, Any


def split_list(list_to_split: List[Any], group_size: int) -> List[Any]:
    result = []
    buffer = []
    i = 1

    for element in list_to_split:
        buffer.append(element)

        if i == group_size:
            result.append(buffer)
            buffer = []
            i = 1
        else:
            i += 1

    result.append(buffer)

    return result
