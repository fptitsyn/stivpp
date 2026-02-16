# 3 - 2
# math.sqrt(x + 5) -- math.sin(x)
import math


def comp(x, n):
    '''
    Docstring for comp
    
    :param x: Description
    :param n: Description

    >>> comp(4, -10)
    3.0

    >>> comp("2", "3")
    Traceback (most recent call last):
        ...
    TypeError: must be real number, not str

    >>> comp([2], 3)
    Traceback (most recent call last):
        ...
    TypeError: '>' not supported between instances of 'list' and 'int'

    >>> comp((2, ), 3)
    Traceback (most recent call last):
        ...
    TypeError: '>' not supported between instances of 'tuple' and 'int'

    >>> comp(2, dict(3))
    Traceback (most recent call last):
        ...
    TypeError: 'int' object is not iterable

    >>> comp({2}, 3)
    Traceback (most recent call last):
        ...
    TypeError: '>' not supported between instances of 'set' and 'int'

    >>> comp(-5, -10)
    0.0

    >>> comp(-10, -50)
    Traceback (most recent call last):
        ...
    ValueError: math domain error

    >>> round(comp(0, 5))
    0

    >>> round(comp(math.pi / 2.5, 5))
    1

    >>> round(comp(-math.pi, 5))
    0

    >>> test_pairs = [(0, 5), (math.pi / 2.5, 5), (-math.pi, 5)]
    >>> results = [round(comp(x, n)) for x, n in test_pairs]
    >>> results
    [0, 1, 0]

    >>> all(-1 <= comp(i, 1000000) <= 1 for i in range(1000))
    True
    '''
    if x > n:
        return math.sqrt(x + 5)
    return math.sin(x)
