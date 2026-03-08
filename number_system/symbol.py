from typing import TypeGuard, TypeVar, Generic, Any, Callable, Self, cast
from functools import partial
from abc import ABC
from .num_types import Field, Ring
from heapq import merge


T = TypeVar("T")
_T_Field = TypeVar("_T_Field", bound=Field)
_T_Ring = TypeVar("_T_Ring", bound=Ring)


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
    def is_var(expr: "Expr") -> TypeGuard["Atom[str]"]:
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
                deg = (0, expr.right.multiorder())
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
            content = (2, (None,))

        return (ReverseOrder(deg), content, op)
        # return (content, op,deg)

    def multiorder(self):
        expr = self

        deg = (1, 1)
        if Expr.is_binop(expr) and expr.op == "**":
            if Expr.is_num(expr.right):
                deg = (1, abs(expr.right.value))
            else:
                deg = (0, expr.right.multiorder())
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
            content = ((2, (None,)),)

        return (ReverseOrder(deg), content, op)
        # return (content, op,deg)


# totally stole this from cmput274
# me when school actually teaches things
class Atom(Expr, Generic[T]):
    def __init__(self, value: T) -> None:
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


class Symbol(ABC, Generic[T]):
    def __init__(
        self, symbol: "Any | Expr | Symbol", num_type: Callable[[Any], T]
    ) -> None:
        # Note: terms should always be reduced
        self.num_type = num_type
        self.expr: Expr
        if isinstance(symbol, Symbol):
            # TODO: check if the return types of .num_type are equal
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
        if isinstance(value, Symbol):
            return self.num_type == value.num_type and self.expr == value.expr
        if type(value) == self.num_type:
            return self._S(value) == self
        return NotImplemented

    @property
    def _S(self) -> Callable[..., Self]:
        """Constructor factory that returns instances of the concrete subclass."""
        return partial(self.__class__, num_type=self.num_type)

    def get_vars(self) -> set[str]:
        if Expr.is_atom(self.expr):
            return set(self.expr.value) if Expr.is_var(self.expr) else set()

        if Expr.is_multiop(self.expr):
            ans = self._S(self.expr.terms[0]).get_vars()
            for i in range(1, len(self.expr.terms)):
                ans |= self._S(self.expr.terms[i]).get_vars()
            return ans

        expr = cast(BinOp, self.expr)
        return self._S(expr.left).get_vars() | self._S(expr.right).get_vars()


class CommRingSymbol(Symbol[_T_Ring]):
    def __init__(
        self, symbol: Any | Expr | Self, num_type: Callable[[Any], _T_Ring]
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

    def _is_compatible(self, value):
        if (
            isinstance(value, type(self))
            and self.num_type == cast(Symbol, value).num_type
        ) or type(value) in [self.num_type, int, float]:
            return True
        # TODO: this is really just sympy compat, we dont wanna support this
        try:
            value + self.num_type(0)  # type: ignore
            value - self.num_type(0)  # type: ignore
            value * self.num_type(0)  # type: ignore
            value / self.num_type(1)  # type: ignore
        except:
            return False
        return True

    def _coerce(self, value: Self | _T_Ring | int | float) -> Self:
        return cast(Self, value) if isinstance(value, type(self)) else self._S(value)

    def _add(self, value: Self | _T_Ring | int | float):
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

        cumm_scale: _T_Ring = self.num_type(0)
        curr: Expr | None = None
        combined: list[Self] = []
        for term in terms:
            scale = self.num_type(1)
            if Expr.is_multiop(term, "*") and Expr.is_num(term.terms[-1]):
                scale = cast(_T_Ring, term.terms[-1].value)
                if len(term.terms) > 2:
                    term = MultiOp("*", *term.terms[:-1])
                else:
                    assert len(term.terms) > 0
                    term = term.terms[0]
            elif Expr.is_num(term):
                scale = cast(_T_Ring, term.value)
                term = Atom(self.num_type(1))

            if curr == None:
                curr = term
                cumm_scale = scale
            elif curr == term:
                cumm_scale += scale
            else:
                if cumm_scale != self.num_type(0):
                    combined.append(cast(Self, self._S(curr) * cumm_scale))
                cumm_scale = scale
                curr = term
        if cumm_scale != self.num_type(0):
            combined.append(cast(Self, self._S(curr) * cumm_scale))

        if len(combined) == 0:
            return self._S(0)
        if len(combined) == 1:
            return combined[0]
        return self._S(MultiOp("+", *(term.expr for term in combined)))

    __add__, __radd__ = _add, _add

    def __sub__(self, value: Self | _T_Ring | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        return self + self.num_type(-1) * value

    def __rsub__(self, value: Self | _T_Ring | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        return cast(Self, value + self.num_type(-1) * self)

    def _mul(self, value: Self | _T_Ring | int | float):
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
            res = self._S(0)
            for term in add_term.expr.terms:
                res += comm_term * self._S(term)
            return cast(Self, res)

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

        cumm_pow: int | CommRingSymbol[int] = 0
        cumm_curr: Self | None = None
        combined: list[Self] = []
        for term in terms:
            term_pow = 1
            if Expr.is_binop(term, "**"):
                term_pow = CommRingSymbol(term.right,int)
                term = term.left
            term = self._S(term)

            if cumm_curr == None:
                cumm_curr = term
                cumm_pow = term_pow
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

    def __neg__(self):
        return self.num_type(-1) * self

    def __pos__(self):
        return self

    def __pow__(self, value: "int | CommRingSymbol[int]") -> Self:
        if (not (isinstance(value, int) or isinstance(value, CommRingSymbol))) or (
            isinstance(value, CommRingSymbol) and not isinstance(value.num_type(0), int)
        ):
            return NotImplemented

        if isinstance(value, CommRingSymbol):
            if Expr.is_num(value.expr):
                value = cast(int, value.expr.value)
            else:
                return self._S(BinOp(self.expr, "**", value.expr))

        if self == self._S(1) or value == 0:
            return self._S(1)
        if self == self._S(0):
            if value < 0:
                raise ZeroDivisionError
            return self._S(0)
        if value == 1:
            return self
        if Expr.is_binop(self.expr, "**"):
            assert Expr.is_num(self.expr.right) and isinstance(self.expr.right, int)
            return cast(
                Self,
                self._S(self.expr.left) ** (self.expr.right * value),
            )

        if Expr.is_num(self.expr):
            return self._S(self.expr.value**value)

        return self._S(BinOp(self.expr, "**", Atom(value)))

    def __hash__(self) -> int:
        return hash(self.expr)

    def evaluate(self, mappings: dict[str, Self | _T_Field | int | float]) -> Self:
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
        if expr.op != "**":
            return op(
                self._S(expr.left).evaluate(mappings),
                self._S(expr.right).evaluate(mappings),
            )
        # this isnt very clean but whatever
        assert Expr.is_num(expr.right) and isinstance(expr.right.value, int)
        return self._S(expr.left).evaluate(mappings) ** expr.right.value


class FieldSymbol(CommRingSymbol[_T_Field]):
    def __truediv__(self, value: Self | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # division by zero
        if value == self._S(0):
            raise ZeroDivisionError

        return cast(Self, self * self._S(value**-1))

    def __rtruediv__(self, value: Self | _T_Field | int | float):
        if not self._is_compatible(value):
            return NotImplemented

        value = self._coerce(value)

        # division by zero
        if self == self._S(0):
            raise ZeroDivisionError
        return cast(Self, value * self._S(self**-1))


__all__ = ["CommRingSymbol", "FieldSymbol", "Symbol"]
