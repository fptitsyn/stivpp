import math
from matplotlib import pyplot as plt


def f(x):
    return math.exp(x)


def g(x):
    if x != 7:
        return 1 / (x - 7)
    return None


def plot(n):
    fx = [i/10 for i in range(-100, n)]
    fy = [f(x) for x in fx]

    gx = [i/10 for i in range(n, 101)]
    gy = [g(x) for x in gx]

    plt.plot(fx, fy, label='exp(x)')
    plt.plot(gx, gy, label='1 / (x - 7)')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    x = int(input("x: "))
    n = int(input("n: " ))
    plot(n)
    