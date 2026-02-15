from fractions import Fraction
from typing import Protocol, Self, Any, TypeVar, Generic, Callable, TypeGuard
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


class Expr:
    @staticmethod
    def is_atom(expr: "Expr") -> TypeGuard["Atom"]:
        return isinstance(expr, Atom)

    @staticmethod
    def is_num(expr: "Expr") -> TypeGuard["Atom"]:
        return isinstance(expr, Atom) and not isinstance(expr.value, str)

    @staticmethod
    def is_var(expr: "Expr") -> TypeGuard["Atom"]:
        return isinstance(expr, Atom) and isinstance(expr.value, str)

    @staticmethod
    def is_binop(expr: "Expr", op=None) -> TypeGuard["BinOp"]:
        return isinstance(expr, BinOp) and (op == None or expr.op == op)

    @staticmethod
    def is_multiop(expr: "Expr", op=None) -> TypeGuard["MultiOp"]:
        return isinstance(expr, MultiOp) and (op == None or expr.op == op)

    # We will not talk about this, it is disgusting and should stay closed
    # for the rest of time, to maintain the safety and prosperity of humanity
    # it is not DRY, soaking wet even, it doesn't even do it's job perfectly
    # but it's well enough
    def binorder(self):
        """
        order is a tuple of
        (deg, op, content)
        if no **, treat as ** 1
        if right of ** is num
          deg is (1, int)
        else
          deg is (0, order)
        op is int
        if is op
          content is (0,...)
        if is var
          content is (1,...)
        if is num
          content is (2,...)
        """
        expr = self

        deg = (1, 1)
        if Expr.is_binop(expr) and expr.op == "**":
            if Expr.is_num(expr.right):
                deg = (1, expr.right.value)
            else:
                deg = (0, expr.right)
            expr = expr.left

        op = None
        content = None
        if Expr.is_multiop(expr):
            if expr.op == "+":
                op = 1
            elif expr.op == "*":
                op = 0
            content = (0, tuple(term.binorder() for term in expr.terms))
        elif Expr.is_var(expr):
            op = 2
            content = (1, (expr.value,))
        elif Expr.is_num(expr):
            op = 2
            content = (2, (expr.value,))

        return (deg, content, op)

    def multiorder(self):
        expr = self

        deg = (1, 1)
        if Expr.is_binop(expr) and expr.op == "**":
            if Expr.is_num(expr.right):
                deg = (1, expr.right.value)
            else:
                deg = (0, expr.right)
            expr = expr.left

        op = None
        content = None
        if Expr.is_multiop(expr):
            if expr.op == "+":
                op = 1
            elif expr.op == "*":
                op = 0
            content = tuple(term.binorder()[1] for term in expr.terms)
        elif Expr.is_var(expr):
            op = 2
            content = ((1, (expr.value,)),)
        elif Expr.is_num(expr):
            op = 2
            content = ((2, (expr.value,)),)

        return (deg, content, op)


# totally stole this from cmput274
# me when school actually teaches things
class Atom(Expr):
    def __init__(self, value) -> None:
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Atom):
            return NotImplemented
        return self.value == value.value

    def __hash__(self) -> int:
        return hash(self.value)


class BinOp(Expr):
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

    def __hash__(self) -> int:
        return hash((self.left, self.op, self.right))


class MultiOp(Expr):
    def __init__(self, op: str, *terms: "Expr") -> None:
        self.op = op
        self.terms = terms

    def __repr__(self) -> str:
        return f"({self.op.join(str(term) for term in self.terms)})"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, MultiOp):
            return NotImplemented
        return self.op == value.op and self.terms == value.terms


T = TypeVar("T")
_T_Field = TypeVar("_T_Field", bound=Field)


class Symbol(ABC, Generic[T]):
    def __init__(
        self, symbol: "Any | Expr | Symbol", num_type: Callable[[Any], T]
    ) -> None:
        # Note: terms should always be reduced
        self.num_type = num_type
        self.expr: Expr
        if isinstance(symbol, Symbol):
            assert symbol.num_type == self.num_type
            self.expr = symbol.expr
        else:
            self.expr = (
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

    @property
    def _S(self) -> Callable[..., Self]:
        """Constructor factory that returns instances of the concrete subclass."""
        return partial(self.__class__, num_type=self.num_type)


class FieldSymbol(Symbol[_T_Field]):
    def __init__(
        self, symbol: "Any | Expr | FieldSymbol", num_type: Callable[[Any], _T_Field]
    ) -> None:
        """
        Implements field operation for symbolic values

        :param symbol:
        :type symbol: `Any | Expr | FieldSymbol`
        :param num_type:
        :type num_type: `Callable[[Any], _T_Field]`

        ## Example
        ```python
        def Q(n):
            return FieldSymbol(n,Fraction)
        print(Q(1)+Q(2)) # 3
        ```
        """
        super().__init__(symbol, num_type)

    def _is_compatible(self, value: object):
        return (
            isinstance(value, FieldSymbol) and self.num_type == value.num_type
        ) or type(value) == self.num_type

    def _coerce(
        self, value: "FieldSymbol[_T_Field] | _T_Field"
    ) -> "FieldSymbol[_T_Field]":
        return value if isinstance(value, FieldSymbol) else self._S(value)

    # TODO: redo this, also reorder the params
    def _combine_atom_values(self, a: Expr, b: Expr, op: str):
        # callers should only call this when a and b are numeric Atoms — enforce at runtime
        if not (Expr.is_num(a) and Expr.is_num(b)):
            raise TypeError("_combine_atom_values expects Atom instances")
        if op == "+":
            return self._S(a.value + b.value)
        if op == "-":
            return self._S(a.value - b.value)
        if op == "*":
            return self._S(a.value * b.value)
        if op == "/":
            return self._S(a.value / b.value)
        if op == "**":
            return self._S(a.value**b.value)
        raise ValueError("unsupported op")

    def _add(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # reorder to cannonical order
        # (assumes commutativity)
        left, right = sorted((self, value), key=lambda x: x.expr.binorder())

        # zero
        if right == self._S(0):
            return left

        # combine numeric atoms
        if Expr.is_num(left.expr) and Expr.is_num(right.expr):
            return self._combine_atom_values(left.expr, right.expr, "+")

        # combine existing +
        # (assumes associativity)
        if Expr.is_multiop(left.expr, "+") or Expr.is_multiop(right.expr, "+"):
            # At least one side is an addition MultiOp
            if Expr.is_multiop(left.expr, "+") and Expr.is_multiop(right.expr, "+"):
                # Merge two addition MultiOps
                # (assumes commutativity)
                merged_terms = merge(
                    left.expr.terms, right.expr.terms, key=lambda x: x.multiorder()
                )
                return self._S(MultiOp("+", *merged_terms))
                # TODO: combine like terms
            else:
                # Add a single term to an addition MultiOp
                if Expr.is_multiop(left.expr, "+"):
                    addition_terms = left.expr.terms
                    single_term = right.expr
                else:  # right_is_addition
                    assert Expr.is_multiop(right.expr, "+")  # this is annoying
                    addition_terms = right.expr.terms
                    single_term = left.expr

                # TODO: insert instead of resorting
                # (assumes commutativity)
                sorted_terms = sorted(
                    addition_terms + (single_term,), key=lambda x: x.multiorder()
                )
                return self._S(MultiOp("+", *sorted_terms))
                # TODO: combine like terms

        # If neither is addition, fall through to other logic

        return self._S(MultiOp("+", left.expr, right.expr))

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

        # reorder to cannonical order
        # (assumes commutativity)
        left, right = sorted((self, value), key=lambda x: x.expr.binorder())

        # zero
        if right == self._S(0):
            return self._S(0)

        # one
        if right == self._S(1):
            return left

        # combine numeric atoms
        if Expr.is_num(left.expr) and Expr.is_num(right.expr):
            return self._combine_atom_values(left.expr, right.expr, "*")

        # combine existing +
        # (assumes associativity)
        if Expr.is_multiop(left.expr, "*") or Expr.is_multiop(right.expr, "*"):
            # At least one side is an addition MultiOp
            if Expr.is_multiop(left.expr, "*") and Expr.is_multiop(right.expr, "*"):
                # Merge two addition MultiOps
                # (assumes commutativity)
                merged_terms = merge(
                    left.expr.terms, right.expr.terms, key=lambda x: x.multiorder()
                )
                return self._S(MultiOp("*", *merged_terms))
                # TODO: combine like terms
            else:
                # Add a single term to an addition MultiOp
                if Expr.is_multiop(left.expr, "*"):
                    addition_terms = left.expr.terms
                    single_term = right.expr
                else:  # right_is_addition
                    assert Expr.is_multiop(right.expr, "*")  # this is annoying
                    addition_terms = right.expr.terms
                    single_term = left.expr

                # TODO: insert instead of resorting
                # (assumes commutativity)
                sorted_terms = sorted(
                    addition_terms + (single_term,), key=lambda x: x.multiorder()
                )
                return self._S(MultiOp("*", *sorted_terms))
                # TODO: combine like terms

        # If neither is addition, fall through to other logic

        # TODO: distributivity

        return self._S(MultiOp("*", left.expr, right.expr))

    __mul__, __rmul__ = _mul, _mul

    def __truediv__(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # division by zero
        if value == self._S(0):
            raise ZeroDivisionError

        return self * self._S(value ** self.num_type(-1))

    def __rtruediv__(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # division by zero
        if self == self._S(0):
            raise ZeroDivisionError

        return value * self._S(self ** self.num_type(-1))

    def __neg__(self):
        return self.num_type(-1) * self

    def __pos__(self):
        return self

    def __pow__(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        if self == self._S(1) or value == self._S(0):
            return self._S(1)

        if Expr.is_num(self.expr) and Expr.is_num(value.expr):
            return self._combine_atom_values(self.expr, value.expr, "**")

        return self._S(BinOp(self.expr, "**", value.expr))

    def __rpow__(self, value: "FieldSymbol[_T_Field]" | _T_Field):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        if value == self._S(1) or self == self._S(0):
            return self._S(1)

        if Expr.is_num(self.expr) and Expr.is_num(value.expr):
            return self._combine_atom_values(value.expr, self.expr, "**")

        return self._S(BinOp(value.expr, "**", self.expr))

    def __hash__(self) -> int:
        return hash(self.expr)


# so apparently there's this thing called sympy
# and it does this but good
# so we're basically reinventing the wheel
# not that we weren't already
# but this is way out of hand for the original scope

Fraction.__repr__ = lambda self: (  # type: ignore
    str(self.numerator // self.denominator)  # type: ignore
    if self.numerator % self.denominator == 0  # type: ignore
    else f"{self.numerator}/{self.denominator}"  # type: ignore
)

__all__ = ["Ring", "Field", "Zmod", "Fraction", "FieldSymbol"]
