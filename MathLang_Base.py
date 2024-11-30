import math


class Fraction:
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator
        self.reduce()

    def __str__(self):
        return f"{self.numerator}/{self.denominator}"

    def reduce(self):
        gcd = math.gcd(self.numerator, self.denominator)
        self.numerator //= gcd
        self.denominator //= gcd

    def __add__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return Fraction(self.numerator * other.denominator + self.denominator * other.numerator,
                            self.denominator * other.denominator)
        raise TypeError("Cannot add Fraction and " + str(type(other)))

    def __sub__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return Fraction(self.numerator * other.denominator - self.denominator * other.numerator,
                            self.denominator * other.denominator)
        raise TypeError("Cannot subtract Fraction and " + str(type(other)))

    def __mul__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return Fraction(self.numerator * other.numerator,
                            self.denominator * other.denominator)
        raise TypeError("Cannot multiply Fraction and " + str(type(other)))

    def __truediv__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return Fraction(self.numerator * other.denominator,
                            self.denominator * other.numerator)
        raise TypeError("Cannot divide Fraction and " + str(type(other)))

    def __rtruediv__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return Fraction(self.denominator * other.numerator,
                            self.numerator * other.denominator)
        raise TypeError("Cannot divide Fraction and " + str(type(other)))

    def reciprocal(self):
        return Fraction(self.denominator, self.numerator)

    def __pow__(self, power):
        return Fraction(self.numerator ** power, self.denominator ** power)

    def __eq__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return self.numerator == other.numerator and self.denominator == other.denominator
        raise TypeError("Cannot compare Fraction and " + str(type(other)))

    def __lt__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return self.numerator * other.denominator < self.denominator * other.numerator
        raise TypeError("Cannot compare Fraction and " + str(type(other)))

    def __gt__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return self.numerator * other.denominator > self.denominator * other.numerator
        raise TypeError("Cannot compare Fraction and " + str(type(other)))

    def __le__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return self.numerator * other.denominator <= self.denominator * other.numerator
        raise TypeError("Cannot compare Fraction and " + str(type(other)))

    def __ge__(self, other):
        if isinstance(other, int):
            other = Fraction(other, 1)
        if isinstance(other, Fraction):
            return self.numerator * other.denominator >= self.denominator * other.numerator
        raise TypeError("Cannot compare Fraction and " + str(type(other)))

    def __ne__(self, other):
        return not (self == other)

    def __abs__(self):
        return Fraction(abs(self.numerator), abs(self.denominator))

    def __neg__(self):
        return Fraction(-self.numerator, self.denominator)


class _Root:
    def __init__(self, num, root=2):
        self.num = num
        self.root = root

    def __str__(self):
        return f"Root({self.num}, {self.root})"

    def __mul__(self, other):
        if isinstance(other, _Root):
            if self.root == other.root:
                return Root(self.num * other.num, self.root)
            else:
                lcm = self.root * math.gcd(self.root, other.root)
                return Root((self.num ** (lcm // self.root)) * (other.num ** (lcm // other.root)), lcm)
        if isinstance(other, int):
            return Root(self.num * (other ** self.root), self.root)
        raise TypeError("Cannot multiple Root and " + str(type(other)))

    def __truediv__(self, other):
        if isinstance(other, _Root):
            if self.root == other.root:
                return Root(self.num / other.num, self.root)
            raise ValueError("Cannot add roots with different roots")
        if isinstance(other, int):
            return Root(self.num / (other ** self.root), self.root)
        raise TypeError("Cannot add Root and " + str(type(other)))

    def __float__(self):
        return math.pow(self.num, 1 / self.root)


class Root:
    def __init__(self, num=None, root=2):
        self.lst = []
        if num:
            r = _Root(num, root)
            self.lst.append(r)

    def append(self, r):
        self.lst.append(r)

    def __str__(self):
        return f"Roots({self.lst})"

    def __mul__(self, other):
        if isinstance(other, Root):
            new = Root()
            for i in self.lst:
                for j in other.lst:
                    new.append(i * j)
            return new
        if isinstance(other, int):
            new = Root()
            for i in self.lst:
                new.append(i * other)
            return new
        raise TypeError("Cannot multiple Root and " + str(type(other)))

    def __truediv__(self, other):
        if isinstance(other, Root):
            new = Root()
            for i in self.lst:
                for j in other.lst:
                    new.append(i / j)
            return new
        if isinstance(other, int):
            new = Root()
            for i in self.lst:
                new.append(i / other)
            return new
        raise TypeError("Cannot add Root and " + str(type(other)))

    def __float__(self):
        return float(self.lst[0])


if __name__ == "__main__":
    a = 1 / Fraction(1, 2)
    a.reduce2()
    print(a)
