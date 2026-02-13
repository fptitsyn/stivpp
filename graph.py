import math
from matplotlib import pyplot as plt


def f(x):
    if x >= -5:
        return math.sqrt(x + 5)
    return None


def g(x):
    return math.sin(x)


def plot(n):
    fx = [i/10 for i in range(-100, n)]
    fy = [f(x) for x in fx]

    gx = [i/10 for i in range(n, 101)]
    gy = [g(x) for x in gx]

    plt.plot(fx, fy, label='sqrt(x + 5)')
    plt.plot(gx, gy, label='sin(x)')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    x = int(input("x: "))
    n = int(input("n: " ))
    plot(n)
    