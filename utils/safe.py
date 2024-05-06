from typing import TypeVar

T = TypeVar("T")


def get(arr: list[T], index: int, default: T) -> T:
    try:
        return arr[index]
    except IndexError:
        return default
