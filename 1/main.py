# 3 - 2
# math.exp(x) -- 1 / (x - 7)
import math


def comp(x, n):
    '''

    >>> comp("2", "3")
    Traceback (most recent call last):
        ...
    TypeError: must be real number, not str

    >>> comp([2], 3)
    Traceback (most recent call last):
        ...
    TypeError: '<' not supported between instances of 'list' and 'int'

    >>> comp((2, ), 3)
    Traceback (most recent call last):
        ...
    TypeError: '<' not supported between instances of 'tuple' and 'int'

    >>> comp(2, dict(3))
    Traceback (most recent call last):
        ...
    TypeError: 'int' object is not iterable

    >>> comp({2}, 3)
    Traceback (most recent call last):
        ...
    TypeError: '<' not supported between instances of 'set' and 'int'

    >>> round(comp(4, 5), 1)
    54.6

    >>> comp(0, 2)
    1.0

    >>> round(comp(-2, 35), 2)
    0.14

    >>> round(comp(10, 5), 1)
    0.3

    >>> round(comp(-7, -10), 2)
    -0.07

    >>> comp(7, 2)
    Traceback (most recent call last):
        ...
    ZeroDivisionError: division by zero

    >>> test_pairs = [(1, 5), (2, 7), (6, 6), (8, 5), (7, 10)]
    >>> results = [round(comp(x, n), 2) for x, n in test_pairs]
    >>> results
    [2.72, 7.39, -1.0, 1.0, 1096.63]

    '''
    if x < n:
        return math.exp(x)
    return 1 / (x - 7)
