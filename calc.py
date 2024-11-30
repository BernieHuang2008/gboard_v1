from math import *


def PointDistance(a: tuple, b: tuple):
    x0, y0 = a
    x1, y1 = b
    res = sqrt(pow(x0 - x1, 2) + pow(y0 - y1, 2))
    return res


def LineSlope(a: tuple, b: tuple):
    if a[0] - b[0] == 0:
        return 0
    return (a[1] - b[1]) / (a[0] - b[0])


def PointOnLine(a: tuple, k, b, error=0):
    return abs(a[1] - k * a[0] + b) <= error


def Vertical(k, a: tuple = (0, 0)):
    nk = -1 / k
    ax, ay = a
    b = ay - ax * nk
    return nk, b
