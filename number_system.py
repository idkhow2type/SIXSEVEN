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


def Zmod(base: int, start=0):
    class _Zmod:
        def __init__(self, num: "int | _Zmod") -> None:
            if isinstance(num, _Zmod):
                assert num.base == base
                self.num = num.num
            else:
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


class ReverseOrder:
    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        # Reverse the "less than" logic
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self) -> str:
        return str(self.value)


class Expr:
    @staticmethod
    def is_atom(expr: "Expr") -> TypeGuard["Atom"]:
        return isinstance(expr, Atom)

    # TODO: make these type guard the type of .value as well
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

    # UPDATE: binorder is really more trouble than it's worth, but multiorder
    # depends on it so can't remove it yet. Maybe one day a man with more
    # courage can rewrite multiorder and put an end to all this
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
                deg = (1, abs(expr.right.value))
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
            # this might not work for everything
            content = (2, (abs(expr.value),))

        return (ReverseOrder(deg), content, op)
        # return (content, op,deg)

    def multiorder(self):
        expr = self

        deg = (1, 1)
        if Expr.is_binop(expr) and expr.op == "**":
            if Expr.is_num(expr.right):
                deg = (1, abs(expr.right.value))
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
            content = ((2, (abs(expr.value),)),)

        return (ReverseOrder(deg), content, op)
        # return (content, op,deg)


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
        ) or type(value) in [self.num_type, int, float]

    def _coerce(
        self, value: "FieldSymbol[_T_Field] | _T_Field | int | float"
    ) -> "FieldSymbol[_T_Field]":
        return value if isinstance(value, FieldSymbol) else self._S(value)

    def _add(self, value: "FieldSymbol[_T_Field]" | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        left, right = self, value

        # side note: this now looks so coughing baby vs hydrogen bomb
        # just a teeny tiny optimisation in an abyss of inefficiencies
        # zero
        if right == self._S(0):
            return left
        if left == self._S(0):
            return right

        # combine numeric atoms
        if Expr.is_num(left.expr) and Expr.is_num(right.expr):
            return self._S(left.expr.value + right.expr.value)

        # combine existing +
        # (assumes associativity)
        left = (
            left
            if Expr.is_multiop(left.expr, "+")
            else self._S(MultiOp("+", left.expr))
        )
        right = (
            right
            if Expr.is_multiop(right.expr, "+")
            else self._S(MultiOp("+", right.expr))
        )

        assert Expr.is_multiop(left.expr, "+") and Expr.is_multiop(right.expr, "+")
        terms = tuple(
            merge(left.expr.terms, right.expr.terms, key=lambda x: x.multiorder())
        )

        cumm_scale: _T_Field = self.num_type(0)
        curr: Expr | None = None
        combined: list[FieldSymbol] = []
        for term in terms:
            scale = self.num_type(1)
            if Expr.is_multiop(term, "*") and Expr.is_num(term.terms[-1]):
                scale = cast(_T_Field, term.terms[-1].value)
                if len(term.terms) > 2:
                    term = MultiOp("*", *term.terms[:-1])
                else:
                    assert len(term.terms) > 0
                    term = term.terms[0]
            elif Expr.is_num(term):
                scale = cast(_T_Field, term.value)
                term = Atom(self.num_type(1))

            if curr == None:
                curr = term
                cumm_scale = scale
            elif curr == term:
                cumm_scale += scale
            else:
                if cumm_scale != self.num_type(0):
                    combined.append(self._S(curr) * cumm_scale)
                cumm_scale = scale
                curr = term
        if cumm_scale != self.num_type(0):
            combined.append(self._S(curr) * cumm_scale)

        if len(combined) == 0:
            return self._S(0)
        if len(combined) == 1:
            return combined[0]
        return self._S(MultiOp("+", *(term.expr for term in combined)))

    __add__, __radd__ = _add, _add

    def __sub__(self, value: "FieldSymbol[_T_Field]" | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        return self + self.num_type(-1) * value

    def __rsub__(self, value: "FieldSymbol[_T_Field]" | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        return cast(FieldSymbol[_T_Field], value + self.num_type(-1) * self)

    def _mul(self, value: "FieldSymbol[_T_Field]" | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        left, right = self, value

        # zero
        if right == self._S(0):
            return self._S(0)
        if left == self._S(0):
            return self._S(0)

        # one
        if right == self._S(1):
            return left
        if left == self._S(1):
            return right

        add_term = None
        comm_term = None
        if Expr.is_multiop(left.expr, "+"):
            add_term = left
            comm_term = right
        elif Expr.is_multiop(right.expr, "+"):
            add_term = right
            comm_term = left
        if add_term != None and comm_term != None:
            assert Expr.is_multiop(add_term.expr, "+")
            # res: list[Expr] = []
            res = self._S(0)
            for term in add_term.expr.terms:
                # res.append((comm_term * self._S(term)).expr)
                res += comm_term * self._S(term)
            # return self._S(MultiOp("+", *res))
            return cast(FieldSymbol[_T_Field], res)

        # combine numeric atoms
        if Expr.is_num(left.expr) and Expr.is_num(right.expr):
            return self._S(left.expr.value * right.expr.value)

        # combine existing *
        # (assumes associativity)
        left = (
            left
            if Expr.is_multiop(left.expr, "*")
            else self._S(MultiOp("*", left.expr))
        )
        right = (
            right
            if Expr.is_multiop(right.expr, "*")
            else self._S(MultiOp("*", right.expr))
        )

        assert Expr.is_multiop(left.expr, "*") and Expr.is_multiop(right.expr, "*")
        terms = tuple(
            merge(left.expr.terms, right.expr.terms, key=lambda x: x.multiorder())
        )

        cumm_pow: _T_Field = self.num_type(0)
        cumm_curr: FieldSymbol | None = None
        combined: list[FieldSymbol] = []
        for term in terms:
            term_pow = self.num_type(1)
            if Expr.is_binop(term, "**") and Expr.is_num(term.right):
                term_pow = cast(_T_Field, term.right.value)
                term = term.left
            term = self._S(term)

            if cumm_curr == None:
                cumm_curr = term
                cumm_pow = term_pow
            elif Expr.is_num(cumm_curr.expr) and Expr.is_num(term.expr):
                cumm_curr *= term
            elif cumm_curr == term:
                cumm_pow += term_pow
            else:
                if cumm_pow != self.num_type(0) and cumm_curr != self._S(1):
                    combined.append(cumm_curr**cumm_pow)
                cumm_pow = term_pow
                cumm_curr = term
        if cumm_pow != self.num_type(0) and cumm_curr != self._S(1):
            combined.append(self._S(cumm_curr) ** cumm_pow)

        if len(combined) == 0:
            return self._S(1)
        if len(combined) == 1:
            return combined[0]
        return self._S(MultiOp("*", *(term.expr for term in combined)))

        # TODO: distributivity

    __mul__, __rmul__ = _mul, _mul

    def __truediv__(self, value: "FieldSymbol[_T_Field]" | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # division by zero
        if value == self._S(0):
            raise ZeroDivisionError

        return cast(FieldSymbol[_T_Field], self * self._S(value ** self.num_type(-1)))

    def __rtruediv__(self, value: "FieldSymbol[_T_Field]" | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # division by zero
        if self == self._S(0):
            raise ZeroDivisionError
        return cast(FieldSymbol[_T_Field], value * self._S(self ** self.num_type(-1)))

    def __neg__(self):
        return self.num_type(-1) * self

    def __pos__(self):
        return self

    def __pow__(self, value: "FieldSymbol[_T_Field]" | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        if self == self._S(1) or value == self._S(0):
            return self._S(1)
        if value == self._S(1):
            return self
        if Expr.is_binop(self.expr, "**"):
            return cast(
                FieldSymbol[_T_Field],
                self._S(self.expr.left) ** (self._S(self.expr.right) * value),
            )

        if Expr.is_num(self.expr) and Expr.is_num(value.expr):
            return self._S(self.expr.value**value.expr.value)

        return self._S(BinOp(self.expr, "**", value.expr))

    def __rpow__(self, value: "FieldSymbol[_T_Field]" | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        if value == self._S(1) or self == self._S(0):
            return self._S(1)
        if self == self._S(1):
            return value
        if Expr.is_binop(value.expr, "**"):
            return self._S(value.expr.left) ** (self._S(value.expr.right) * self)

        if Expr.is_num(self.expr) and Expr.is_num(value.expr):
            return self._S(value.expr.value**self.expr.value)

        return self._S(BinOp(value.expr, "**", self.expr))

    def __hash__(self) -> int:
        return hash(self.expr)

    def evaluate(
        self, mappings: dict[str, "FieldSymbol[_T_Field]" | _T_Field | int | float]
    ) -> "FieldSymbol[_T_Field]":
        if Expr.is_atom(self.expr):
            return self._S(mappings.get(self.expr.value, self.expr))

        expr = cast(BinOp | MultiOp, self.expr)
        op = {
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y,
            "**": lambda x, y: x**y,
        }[expr.op]

        if Expr.is_multiop(self.expr):
            ans = self._S(self.expr.terms[0]).evaluate(mappings)
            for i in range(1, len(self.expr.terms)):
                ans = op(ans, self._S(self.expr.terms[i]).evaluate(mappings))
            return ans

        expr = cast(BinOp, self.expr)
        return op(
            self._S(expr.left).evaluate(mappings),
            self._S(expr.right).evaluate(mappings),
        )


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
