from fractions import Fraction
from typing import Protocol, Self, Any, TypeVar, Generic, Callable, TypeGuard, cast
from abc import ABC
from functools import partial
from heapq import merge


# TODO: maybe make these support ints and floats
class Ring(Protocol):
    def __add__(self, other: Self, /) -> Self: ...
    def __radd__(self, other: Self, /) -> Self: ...
    def __sub__(self, other: Self, /) -> Self: ...
    def __rsub__(self, other: Self, /) -> Self: ...
    def __mul__(self, other: Self, /) -> Self: ...
    def __rmul__(self, other: Self, /) -> Self: ...


class Field(Ring, Protocol):
    def __truediv__(self, other: Self, /) -> Self: ...
    def __rtruediv__(self, other: Self, /) -> Self: ...


# * partial init with proper generics
# from typing import TypeVar, Generic, Callable

# T=TypeVar("T")

# class Base(Generic[T]):
#     def __init__(self, arg:T, arg2:int) -> None:
#         self.val=arg
#         self.val2=arg2

#     @staticmethod
#     def make(arg: float):
#         f: Callable[[int]] = lambda arg2: Base(arg, arg2)
#         return f

# b=Base.make(1)
# b(2)


class _Zmod:
    def __init__(self, num: "int | _Zmod", base: int, start=0) -> None:
        if isinstance(num, _Zmod):
            assert num.base == base
            self.num = num.num
        else:
            self.num: int = (num) % (base)
        self.base = base
        self.start = start
        for i in range(base):
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
        if isinstance(other, _Zmod) and other.base == self.base:
            return self.num == other.num
        return False

    def _add(self, other: "_Zmod | int") -> "_Zmod":
        if type(other) is int:
            return _Zmod(((self.num + other) % (self.base)), self.base)
        if isinstance(other, _Zmod) and other.base == self.base:
            return _Zmod(((self.num + other.num) % (self.base)), self.base)
        return NotImplemented

    __add__, __radd__ = _add, _add

    def _mul(self, other: "_Zmod | int") -> "_Zmod":
        if type(other) is int:
            return _Zmod(((self.num * other) % (self.base)), self.base)
        if isinstance(other, _Zmod) and other.base == self.base:
            return _Zmod(((self.num * other.num) % (self.base)), self.base)
        return NotImplemented

    __mul__, __rmul__ = _mul, _mul

    def __sub__(self, other: "_Zmod | int") -> "_Zmod":
        if type(other) is int:
            return _Zmod(((self.num - other) % (self.base)), self.base)
        if isinstance(other, _Zmod) and other.base == self.base:
            return _Zmod(((self.num - other.num) % (self.base)), self.base)
        return NotImplemented

    def __rsub__(self, other: "_Zmod | int") -> "_Zmod":
        if type(other) is int:
            return _Zmod(((other - self.num) % (self.base)), self.base)
        if isinstance(other, _Zmod) and other.base == self.base:
            return _Zmod(((other.num - self.num) % (self.base)), self.base)
        return NotImplemented

    def __truediv__(self, other: "_Zmod | int") -> "_Zmod":
        if type(other) is int:
            return _Zmod(
                ((self.num * _Zmod(other, self.base).inv) % (self.base)), self.base
            )
        if isinstance(other, _Zmod) and other.base == self.base:
            return _Zmod(((self.num * other.inv) % (self.base)), self.base)
        return NotImplemented

    def __rtruediv__(self, other: "_Zmod | int") -> "_Zmod":
        if type(other) is int:
            return _Zmod(((other * self.inv) % (self.base)), self.base)
        if isinstance(other, _Zmod) and other.base == self.base:
            return _Zmod(((other.num * self.inv) % (self.base)), self.base)
        return NotImplemented

    def __neg__(self) -> "_Zmod":
        return _Zmod((-self.num) % (self.base), self.base)

    def __pos__(self) -> "_Zmod":
        return _Zmod(self.num, self.base)


def Zmod(base: int, start=0):
    return partial(Zmod, base=base, start=start)


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

__all__ = ["Ring", "Field", "Zmod", "Fraction", "_Zmod"]
