from fractions import Fraction
from typing import Protocol, Self, Callable, Any


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


class Atom:
    def __init__(self, value) -> None:
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)


class BinOp:
    def __init__(self, left: "Expr", op: str, right: "Expr") -> None:
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"({str(self.left) + self.op + str(self.right)})"


Expr = Atom | BinOp

class Symbol:
    def __init__(self, symbol: Any | Expr, reducer: Callable[[Expr], Expr]) -> None:
        # Note: terms should always be reduced
        self.expr: Expr = (
            symbol if isinstance(symbol, Expr) else Atom(symbol)
        )
        self.reducer = reducer

    def __repr__(self) -> str:
        return str(self.expr)

    def __eq__(self, value: object) -> bool:
        return (
            type(value) == Symbol
            and self.expr == value.expr
            and self.reducer == value.reducer
        )

    def _compute(self, value: "Symbol | Any", op: str, swap=False):
        if type(value) == Symbol:
            if value.reducer != self.reducer:
                raise ValueError
            left = self.expr
            right = value.expr
        else:
            left = self.expr
            right = Atom(value)

        if swap:
            left, right = right, left

        return Symbol(self.reducer(BinOp(left, op, right)), self.reducer)

    def __add__(self, value: "Symbol | Any"):
        return self._compute(value, "+")

    def __radd__(self, value: "Symbol | Any"):
        return self._compute(value, "+", swap=True)

    def __sub__(self, value: "Symbol | Any"):
        return self._compute(value, "-")

    def __rsub__(self, value: "Symbol | Any"):
        return self._compute(value, "-", swap=True)

    def __mul__(self, value: "Symbol | Any"):
        return self._compute(value, "*")

    def __rmul__(self, value: "Symbol | Any"):
        return self._compute(value, "*", swap=True)

    def __matmul__(self, value: "Symbol | Any"):
        return self._compute(value, "@")

    def __rmatmul__(self, value: "Symbol | Any"):
        return self._compute(value, "@", swap=True)


def basic_generic_reducer(expr: Expr) -> Expr:
    if type(expr) == Atom:
        return expr
    assert type(expr) == BinOp
    left = basic_generic_reducer(expr.left)
    right = basic_generic_reducer(expr.right)
    if type(left) == Atom and type(right) == Atom:
        try:
            ops = {
                "+": lambda x, y: x + y,
                "-": lambda x, y: x - y,
                "*": lambda x, y: x * y,
            }
            return Atom(ops[expr.op](left.value, right.value))
        except:
            pass

    # Identity and annihilator rules
    if expr.op == "+":
        if type(left) == Atom and left.value == 0:
            return right
        if type(right) == Atom and right.value == 0:
            return left
    elif expr.op == "*":
        if type(left) == Atom and left.value == 1:
            return right
        if type(right) == Atom and right.value == 1:
            return left
        if (type(left) == Atom and left.value == 0) or (type(right) == Atom and right.value == 0):
            return Atom(0)

    return BinOp(left, expr.op, right)


Fraction.__repr__ = lambda self: (
    str(self.numerator // self.denominator)
    if self.numerator % self.denominator == 0
    else f"{self.numerator}/{self.denominator}"
)

__all__ = ["Ring", "Field", "Zmod", "Fraction", "Symbol", "basic_generic_reducer"]
