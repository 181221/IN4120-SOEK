from typing import Iterator


def intersection(p1: Iterator[str], p2: Iterator[str]) -> Iterator[str]:
    el1 = next(p1, None)
    el2 = next(p2, None)
    while el1 is not None and el2 is not None:
        if el1 == el2:
            yield el1
            el1 = next(p1, None)
            el2 = next(p2, None)
        elif el1 < el2:
            el1 = next(p1, None)
        else:
            el2 = next(p2, None)


test = intersection(iter(['a', 'b','c','d','e','f','i','k']), iter(['a', 'b', 'b', 'c','e','f','k']))

for t in test:
    print(t)