from typing import TypeVar, Generic, Sequence, overload, Callable, Any, cast, Literal
from .number_system import *
from .config import CONFIG

_T_Ring = TypeVar("_T_Ring", bound=Ring)
_T_Field = TypeVar("_T_Field", bound=Field)
_T_In = TypeVar("_T_In")
_T_RingStatic = TypeVar("_T_RingStatic", bound=Ring)


class Vector(Generic[_T_Ring]):
    @overload
    def __init__(self, *data: _T_Ring, num_type: None = None) -> None: ...
    @overload
    def __init__(self, *data: _T_In, num_type: Callable[[_T_In], _T_Ring]) -> None: ...

    def __init__(
        self, *data: Any, num_type: Callable[[_T_In], _T_Ring] | None = None
    ) -> None:
        self._data = [(num_type(item) if num_type else item) for item in data]

    def __repr__(self) -> str:
        match CONFIG["repr_type"]:
            case "default":
                return f"({' '.join(str(i) for i in self._data)})"
            case "latex":
                return f"\\begin{{pmatrix}}{'\\\\'.join(str(i) for i in self._data)}\\end{{pmatrix}}"

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, i: int):
        return self._data[i]

    def __iter__(self):
        return iter(self._data)

    def _add(self, other: "Vector[_T_Ring]") -> "Vector[_T_Ring]":
        if len(self) != len(other):
            raise ValueError
        return Vector(*(a + b for a, b in zip(self, other)))

    __add__, __radd__ = _add, _add

    def __sub__(self, other: "Vector[_T_Ring]") -> "Vector[_T_Ring]":
        if len(self) != len(other):
            raise ValueError
        return Vector(*(a - b for a, b in zip(self, other)))

    def __rsub__(self, other: "Vector[_T_Ring]") -> "Vector[_T_Ring]":
        if len(self) != len(other):
            raise ValueError
        return Vector(*(b - a for a, b in zip(self, other)))

    def _mul(self, other: _T_Ring) -> "Vector[_T_Ring]":
        return Vector(*(item * other for item in self._data))

    __mul__, __rmul__ = _mul, _mul


def dot(vec_a: Vector[_T_Ring], vec_b: Vector[_T_Ring]) -> _T_Ring:
    if len(vec_a) != len(vec_b):
        raise ValueError

    ans: _T_Ring = cast(_T_Ring, 0)
    for a, b in zip(vec_a, vec_b):
        ans += a * b
    return ans


class Matrix(Generic[_T_Ring]):
    @overload
    def __init__(self, *data: Sequence[_T_Ring], num_type: None = None) -> None: ...
    @overload
    def __init__(
        self, *data: Sequence[_T_In], num_type: Callable[[_T_In], _T_Ring]
    ) -> None: ...

    def __init__(
        self, *data: Sequence[Any], num_type: Callable[[Any], _T_Ring] | None = None
    ) -> None:
        self._data = tuple(
            tuple((num_type(item) if num_type else item) for item in row)
            for row in data
        )
        self.rows = len(data)
        self.cols = len(data[0])
        self.num_type = num_type or type(self[0, 0])

    def __repr__(self):
        match CONFIG["repr_type"]:
            case "default":
                max_width = 0
                for row in self._data:
                    for item in row:
                        max_width = max(max_width, len(str(item)))

                ans = ""
                for row in self._data:
                    ans += "( "
                    for item in row:
                        ans += str(item).ljust(max_width) + " "
                    ans += ")\n"
                return ans[:-1]
            case "latex":
                return "\\begin{pmatrix}"+"\\\\".join('&'.join(str(i) for i in row) for row in self._data)+"\\end{pmatrix}"

    def __getitem__(self, pos: tuple):
        row, col = pos
        return self._data[row][col]

    def _add(self, other: "Matrix"):
        return Matrix(
            *(
                tuple(a + b for a, b in zip(row_self, row_other))
                for row_self, row_other in zip(self._data, other._data)
            ),
        )

    __add__, __radd__ = _add, _add

    def __sub__(self, other: "Matrix"):
        return Matrix(
            *(
                tuple(a - b for a, b in zip(row_self, row_other))
                for row_self, row_other in zip(self._data, other._data)
            ),
        )

    def __rsub__(self, other: "Matrix"):
        return Matrix(
            *(
                tuple(b - a for a, b in zip(row_self, row_other))
                for row_self, row_other in zip(self._data, other._data)
            ),
        )

    def row(self, i: int) -> Vector[_T_Ring]:
        return Vector(*self._data[i])

    def col(self, j: int) -> Vector[_T_Ring]:
        return Vector(*(self._data[i][j] for i in range(self.rows)))

    def _mul(self, other: _T_Ring):
        return Matrix(
            *([other * item for item in row] for row in self._data),
        )

    __mul__, __rmul__ = _mul, _mul

    def __matmul__(self, other: "Matrix"):
        if self.cols != other.rows:
            raise ValueError

        return Matrix(
            *[
                [dot(self.row(i), other.col(j)) for j in range(other.cols)]
                for i in range(self.rows)
            ],
        )

    def __rmatmul__(self, other: "Matrix"):
        if other.cols != self.cols:
            raise ValueError

        return Matrix(
            *[
                [dot(other.row(i), self.col(j)) for j in range(self.cols)]
                for i in range(other.rows)
            ],
        )

    @staticmethod
    def ident(
        size: int, num_type: Callable[[int], _T_RingStatic] = float
    ) -> "Matrix[_T_RingStatic]":
        data = tuple(tuple(int(i == j) for j in range(size)) for i in range(size))
        return Matrix(*data, num_type=num_type)

    def __pow__(
        self: "Matrix[_T_Field]", other: Literal["T", -1]
    ) -> "Matrix[_T_Ring] | Matrix[_T_Field]":
        match other:
            case "T":
                return Matrix(
                    *(
                        [self._data[j][i] for j in range(self.rows)]
                        for i in range(self.cols)
                    )
                )

            case -1:
                if self.rows != self.cols:
                    raise ValueError

                from .gaussian_elim import to_rref

                ops = to_rref(self, allow_zeroes=False)[1]
                inv = Matrix.ident(
                    self.rows, cast("Callable[[int], _T_Field]", self.num_type)
                )
                for op in ops:
                    inv = op.apply(inv)
                return inv

        return NotImplemented

    def null(self) -> list[Vector]:
        params = {}
        pivots = {}
        for i in range(self.rows):
            for j in range(self.cols):
                if self[i, j] == self.num_type(1):
                    pivots[j] = i
                    break
        for j in range(self.cols):
            if j not in pivots:
                params.setdefault(j, [self.num_type(0)] * self.cols)[j] = self.num_type(
                    1
                )
            else:
                for j_ in range(j + 1, self.cols):
                    if self[pivots[j], j_] != self.num_type(0):
                        params.setdefault(j_, [self.num_type(0)] * self.cols)[j] = (
                            -self[pivots[j], j_]
                        )
        return [Vector(*params[k]) for k in params]


T = "T"

__all__ = ["Vector", "Matrix", "T"]
