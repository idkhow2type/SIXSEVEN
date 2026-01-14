from fractions import Fraction
from typing import Protocol, Self

class Ring(Protocol):
    def __add__(self, other: Self, /) -> Self: ...
    def __radd__(self, other: Self, /) -> Self: ...
    def __sub__(self, other: Self, /) -> Self: ...
    def __rsub__(self, other: Self, /) -> Self: ...
    def __mul__(self, other: Self, /) -> Self: ...
    def __rmul__(self, other: Self, /) -> Self: ...

# TODO: this obviously doesnt support ints, and floats look ugly, so make a real type wrapper
class Field(Ring, Protocol):
    def __truediv__(self, other: Self, /) -> Self: ...
    def __rtruediv__(self, other: Self, /) -> Self: ...


def Zmod(base: int, start=0):
    class _Zmod:
        def __init__(self, num: int) -> None:
            self.num: int = (num) % (base)
            self.base = base
            for i in range(base):
                if ((self.num * i) % (self.base)) == 1:
                    self.inv = i
                    break

        def __repr__(self) -> str:
            ans = self.num
            while abs(start - ans) >= base:
                ans += abs(start - self.num) // (start - self.num) * self.base
            return str(ans)

        def __eq__(self, other) -> bool:
            if type(other) is int:
                return self.num == ((other) % (self.base))
            if isinstance(other, _Zmod) and other.base == self.base:
                return self.num == other.num
            return False

        def _add(self, other: "_Zmod | int") -> "_Zmod":
            if type(other) is int:
                return _Zmod(((self.num + other) % (self.base)))
            if isinstance(other, _Zmod) and other.base == self.base:
                return _Zmod(((self.num + other.num) % (self.base)))
            return NotImplemented

        __add__, __radd__ = _add, _add

        def _mul(self, other: "_Zmod | int") -> "_Zmod":
            if type(other) is int:
                return _Zmod(((self.num * other) % (self.base)))
            if isinstance(other, _Zmod) and other.base == self.base:
                return _Zmod(((self.num * other.num) % (self.base)))
            return NotImplemented

        __mul__, __rmul__ = _mul, _mul

        def __sub__(self, other: "_Zmod | int") -> "_Zmod":
            if type(other) is int:
                return _Zmod(((self.num - other) % (self.base)))
            if isinstance(other, _Zmod) and other.base == self.base:
                return _Zmod(((self.num - other.num) % (self.base)))
            return NotImplemented

        def __rsub__(self, other: "_Zmod | int") -> "_Zmod":
            if type(other) is int:
                return _Zmod(((other - self.num) % (self.base)))
            if isinstance(other, _Zmod) and other.base == self.base:
                return _Zmod(((other.num - self.num) % (self.base)))
            return NotImplemented

        def __truediv__(self, other: "_Zmod | int") -> "_Zmod":
            if type(other) is int:
                return _Zmod(((self.num * _Zmod(other).inv) % (self.base)))
            if isinstance(other, _Zmod) and other.base == self.base:
                return _Zmod(((self.num * other.inv) % (self.base)))
            return NotImplemented

        def __rtruediv__(self, other: "_Zmod | int") -> "_Zmod":
            if type(other) is int:
                return _Zmod(((other * self.inv) % (self.base)))
            if isinstance(other, _Zmod) and other.base == self.base:
                return _Zmod(((other.num * self.inv) % (self.base)))
            return NotImplemented

        def __neg__(self) -> "_Zmod":
            return _Zmod((-self.num) % (self.base))

        def __pos__(self) -> "_Zmod":
            return _Zmod(self.num)

    return _Zmod


Fraction.__repr__ = lambda self: (
    str(self.numerator // self.denominator)
    if self.numerator % self.denominator == 0
    else f"{self.numerator}/{self.denominator}"
)

__all__ = ["Ring","Field", "Zmod", "Fraction"]
