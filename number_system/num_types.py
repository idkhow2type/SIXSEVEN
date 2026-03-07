from fractions import Fraction
from typing import Protocol, Self, Callable, cast, ClassVar
from functools import partial


# TODO: maybe make these support ints and floats
class Ring(Protocol):
    def __add__(self, other: Self, /) -> Self: ...
    def __radd__(self, other: Self, /) -> Self: ...
    def __sub__(self, other: Self, /) -> Self: ...
    def __rsub__(self, other: Self, /) -> Self: ...
    def __mul__(self, other: Self, /) -> Self: ...
    def __rmul__(self, other: Self, /) -> Self: ...
    def __pow__(self, other: int, /) -> Self: ...


class Field(Ring, Protocol):
    def __truediv__(self, other: Self, /) -> Self: ...
    def __rtruediv__(self, other: Self, /) -> Self: ...


class Zmod(Ring):
    base: ClassVar[int]
    start: ClassVar[int]

    @staticmethod
    def bind(base: int, start=0) -> type["Zmod"]:
        return type(f"Z{base}", (Zmod,), {"base": base, "start": start})

    def __init__(self, num: "int | Zmod") -> None:
        assert isinstance(self.base, int)
        if isinstance(num, Zmod):
            assert num.base == self.base
            self.num = num.num
        else:
            self.num: int = (num) % (self.base)
        for i in range(self.base):
            if ((self.num * i) % (self.base)) == 1:
                self.inv = i
                break

    def __repr__(self) -> str:
        ans = self.num
        while abs(self.start - ans) >= self.base:
            ans += abs(self.start - self.num) // (self.start - self.num) * self.base
        return str(ans)

    def __eq__(self, other) -> bool:
        if type(other) is int:
            return self.num == ((other) % (self.base))
        if isinstance(other, Zmod) and other.base == self.base:
            return self.num == other.num
        return False

    def _add(self, other: "Zmod | int") -> Self:
        if type(other) is int:
            return type(self)(((self.num + other) % (self.base)))
        if isinstance(other, Zmod) and other.base == self.base:
            return type(self)(((self.num + other.num) % (self.base)))
        return NotImplemented

    __add__, __radd__ = _add, _add

    def _mul(self, other: "Zmod | int") -> Self:
        if type(other) is int:
            return type(self)(((self.num * other) % (self.base)))
        if isinstance(other, Zmod) and other.base == self.base:
            return type(self)(((self.num * other.num) % (self.base)))
        return NotImplemented

    __mul__, __rmul__ = _mul, _mul

    def __sub__(self, other: "Zmod | int"):
        if type(other) is int:
            return type(self)(((self.num - other) % (self.base)))
        if isinstance(other, Zmod) and other.base == self.base:
            return type(self)(((self.num - other.num) % (self.base)))
        return NotImplemented

    def __rsub__(self, other: "Zmod | int"):
        if type(other) is int:
            return type(self)(((other - self.num) % (self.base)))
        if isinstance(other, Zmod) and other.base == self.base:
            return type(self)(((other.num - self.num) % (self.base)))
        return NotImplemented

    def __truediv__(self, other: "Zmod | int"):
        if type(other) is int:
            return type(self)(((self.num * type(self)(other).inv) % (self.base)))
        if isinstance(other, Zmod) and other.base == self.base:
            return type(self)(((self.num * other.inv) % (self.base)))
        return NotImplemented

    def __rtruediv__(self, other: "Zmod | int"):
        if type(other) is int:
            return type(self)(((other * self.inv) % (self.base)))
        if isinstance(other, Zmod) and other.base == self.base:
            return type(self)(((other.num * self.inv) % (self.base)))
        return NotImplemented
    
    def __pow__(self, other: int) -> Self:
        ans=type(self)(1)
        for _ in range(other):
            ans*=self
        return ans

    def __neg__(self) -> "Zmod":
        return type(self)((-self.num) % (self.base))

    def __pos__(self) -> "Zmod":
        return type(self)(self.num)

    def __abs__(self):
        return self.num

    def __hash__(self) -> int:
        return hash(self.num)


# so apparently there's this thing called sympy
# and it does this but good
# so we're basically reinventing the wheel
# not that we weren't already
# but this is way out of hand for the original scope

Fraction.__repr__ = lambda self: (
    str(self.numerator // self.denominator)
    if self.numerator % self.denominator == 0
    else f"{self.numerator}/{self.denominator}"
)

__all__ = ["Ring", "Field", "Fraction", "Zmod"]
