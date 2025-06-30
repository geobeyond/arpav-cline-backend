from itertools import islice


def batched(iterable, n):
    """Custom implementation of `itertools.batched()`.

    This is a custom implementation of `itertools.batched()`, which is only available
    on Python 3.12+. This is copied verbatim from the python docs at:

    https://docs.python.org/3/library/itertools.html#itertools.batched

    """
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch
