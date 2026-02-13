from fractions import Fraction
from typing import Protocol, Self, Any, TypeVar, Generic, Callable, overload
from abc import ABC, abstractmethod


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


# totally stole this from cmput274
# me when school actually teaches things
class Atom:
    def __init__(self, value) -> None:
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Atom):
            return NotImplemented
        return self.value == value.value


class BinOp:
    def __init__(self, left: "Expr", op: str, right: "Expr") -> None:
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"({str(self.left) + self.op + str(self.right)})"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, BinOp):
            return NotImplemented
        return (
            self.op == value.op
            and self.left == value.left
            and self.right == value.right
        )


Expr = Atom | BinOp

T = TypeVar("T")
_T_Field = TypeVar("_T_Field", bound=Field)


class Symbol(ABC, Generic[T]):
    def __init__(
        self, symbol: "Any | Expr | Symbol", num_type: Callable[[Any], T]
    ) -> None:
        # Note: terms should always be reduced
        self.num_type = num_type
        if isinstance(symbol, Symbol):
            assert symbol.num_type == self.num_type
            self.expr = symbol.expr
        else:
            self.expr: Expr = (
                symbol
                if isinstance(symbol, Expr)
                else Atom(symbol if isinstance(symbol, str) else self.num_type(symbol))
            )

    def __repr__(self) -> str:
        return str(self.expr)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Symbol):
            return NotImplemented
        return self.num_type == value.num_type and self.expr == value.expr


class FieldSymbol(Symbol[_T_Field]):
    def __init__(
        self, symbol: "Any | Expr | FieldSymbol", num_type: Callable[[Any], _T_Field]
    ) -> None:
        super().__init__(symbol, num_type)

    # --- small helpers to remove repetition ---
    def _is_compatible(self, value: object):
        return (
            isinstance(value, FieldSymbol) and self.num_type == value.num_type
        ) or type(value) == self.num_type

    def _coerce(
        self, value: "FieldSymbol[_T_Field] | _T_Field"
    ) -> "FieldSymbol[_T_Field]":
        return (
            value
            if isinstance(value, FieldSymbol)
            else FieldSymbol(value, self.num_type)
        )

    def _is_atom(self, expr: Expr) -> bool:
        return isinstance(expr, Atom)

    def _atom_is_number(self, expr: Expr) -> bool:
        # ensure expr is Atom before accessing .value
        return isinstance(expr, Atom) and not isinstance(expr.value, str)

    def _is_zero(self, expr: Expr) -> bool:
        # ensure expr is Atom before accessing .value
        return isinstance(expr, Atom) and expr.value == self.num_type(0)

    def _is_one(self, expr: Expr) -> bool:
        # ensure expr is Atom before accessing .value
        return isinstance(expr, Atom) and expr.value == self.num_type(1)

    def _both_atom_numbers(self, a: Expr, b: Expr) -> bool:
        return self._atom_is_number(a) and self._atom_is_number(b)

    def _combine_atom_values(self, a: Expr, b: Expr, op: str):
        # callers should only call this when a and b are numeric Atoms — enforce at runtime
        if not isinstance(a, Atom) or not isinstance(b, Atom):
            raise TypeError("_combine_atom_values expects Atom instances")
        if op == "+":
            return FieldSymbol(a.value + b.value, self.num_type)
        if op == "-":
            return FieldSymbol(a.value - b.value, self.num_type)
        if op == "*":
            return FieldSymbol(a.value * b.value, self.num_type)
        if op == "/":
            return FieldSymbol(a.value / b.value, self.num_type)
        raise ValueError("unsupported op")

    def order(self):
        """
        order from least to most
        number atom
        string atom
        expr
        """
        if isinstance(self.expr, Atom):
            # actually fields aren't neccessarilly well ordered,
            # so this doesn't compare number atoms to each other
            # this is fine as they'll be combined already
            return (int(isinstance(self.expr.value, str)), self.expr.value)
        return (2, -1)

    # --- arithmetic operations ---
    def _add(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # additive identities
        if self._is_zero(self.expr):
            return value
        if self._is_zero(value.expr):
            return self

        # combine numeric atoms
        if self._both_atom_numbers(self.expr, value.expr):
            return self._combine_atom_values(self.expr, value.expr, "+")


        # commutativity
        left, right = sorted((self, value), key=lambda x: x.order())

        """
        right is number atom then left is number atom => combined already => impossible
        right is string atom then left is string atom or number atom
        right is expr then left is atom or expr
        """

        # associativity
        if isinstance(right.expr, BinOp) and right.expr.op == "+":
            return (
                left + FieldSymbol(right.expr.left, num_type=self.num_type)
            ) + FieldSymbol(right.expr.right, num_type=self.num_type)

        return FieldSymbol(BinOp(left.expr, "+", right.expr), self.num_type)

    __add__, __radd__ = _add, _add

    def __sub__(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        return self + self.num_type(-1) * value

    def __rsub__(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        return value + self.num_type(-1) * self

    def _mul(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # zero
        if self._is_zero(self.expr) or self._is_zero(value.expr):
            return FieldSymbol(self.num_type(0), self.num_type)

        # one
        if self._is_one(self.expr):
            return value
        if self._is_one(value.expr):
            return self


        # combine numeric atoms
        if self._both_atom_numbers(self.expr, value.expr):
            return self._combine_atom_values(self.expr, value.expr, "*")
        
        # commutativity
        left, right = sorted((self, value), key=lambda x: x.order())

        # associativity
        if isinstance(right.expr, BinOp) and right.expr.op == "*":
            return (
                left + FieldSymbol(right.expr.left, num_type=self.num_type)
            ) + FieldSymbol(right.expr.right, num_type=self.num_type)

        return FieldSymbol(BinOp(left.expr, "*", right.expr), self.num_type)

    __mul__, __rmul__ = _mul, _mul

    def __truediv__(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # division by zero
        if self._is_zero(value.expr):
            raise ZeroDivisionError

        # x / 1 -> x
        if self._is_one(value.expr):
            return self

        # 0 / x -> 0
        if self._is_zero(self.expr):
            return FieldSymbol(self.num_type(0), self.num_type)

        # x / x -> 1
        if self.expr == value.expr:
            return FieldSymbol(self.num_type(1), self.num_type)

        # combine numeric atoms
        if self._both_atom_numbers(self.expr, value.expr):
            return self._combine_atom_values(self.expr, value.expr, "/")

        return FieldSymbol(BinOp(self.expr, "/", value.expr), self.num_type)

    def __rtruediv__(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # division by zero
        if self._is_zero(self.expr):
            raise ValueError

        # 1 / x -> x when x == 1 handled below
        if self._is_one(self.expr):
            return value

        # 0 / x -> 0
        if self._is_zero(value.expr):
            return FieldSymbol(self.num_type(0), self.num_type)

        # x / x -> 1
        if self.expr == value.expr:
            return FieldSymbol(self.num_type(1), self.num_type)

        # combine numeric atoms
        if self._both_atom_numbers(self.expr, value.expr):
            return self._combine_atom_values(value.expr, self.expr, "/")

        return FieldSymbol(BinOp(value.expr, "/", self.expr), self.num_type)

    def __neg__(self):
        return self.num_type(-1) * self


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

__all__ = ["Ring", "Field", "Zmod", "Fraction", "FieldSymbol"]
