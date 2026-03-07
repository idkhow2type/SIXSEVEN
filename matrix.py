from typing import TypeVar, Generic, Sequence, Callable, Any, cast, Literal, overload
from .number_system import *
from .roots import *
from .config import CONFIG

_T_Ring = TypeVar("_T_Ring", bound=Ring)
_T_Field = TypeVar("_T_Field", bound=Field)
_T_In = TypeVar("_T_In")
_T_RingStatic = TypeVar("_T_RingStatic", bound=Ring)


class Vector(Generic[_T_Ring], Sequence):
    def __init__(
        self, *data: Any, num_type: Callable[[_T_In], _T_Ring] | None = None
    ) -> None:
        self.num_type = num_type or (
            type(data[0])
            if CONFIG["num_type"]["missing"] == "infer"
            else cast(Callable[[Any], _T_Ring], CONFIG["num_type"]["default"])
        )
        self._data = tuple(self.num_type(item) for item in data)

    def __repr__(self) -> str:
        match CONFIG["repr_type"]:
            case "default":
                return f"({' '.join(str(i) for i in self._data)})"
            case "latex":
                return f"\\begin{{pmatrix}}{'\\\\'.join(str(i) for i in self._data)}\\end{{pmatrix}}"

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, i):
        return self._data[i]

    def __iter__(self):
        return iter(self._data)

    def _add(self, other: "Vector[_T_Ring]") -> "Vector[_T_Ring]":
        if len(self) != len(other):
            raise ValueError
        return Vector(*(a + b for a, b in zip(self, other)), num_type=self.num_type)

    __add__, __radd__ = _add, _add

    def __sub__(self, other: "Vector[_T_Ring]") -> "Vector[_T_Ring]":
        if len(self) != len(other):
            raise ValueError
        return Vector(*(a - b for a, b in zip(self, other)), num_type=self.num_type)

    def __rsub__(self, other: "Vector[_T_Ring]") -> "Vector[_T_Ring]":
        if len(self) != len(other):
            raise ValueError
        return Vector(*(b - a for a, b in zip(self, other)), num_type=self.num_type)

    def _mul(self, other: _T_Ring) -> "Vector[_T_Ring]":
        return Vector(*(item * other for item in self._data), num_type=self.num_type)

    __mul__, __rmul__ = _mul, _mul


def dot(vec_a: Vector[_T_Ring], vec_b: Vector[_T_Ring]) -> _T_Ring:
    if len(vec_a) != len(vec_b):
        raise ValueError

    ans: _T_Ring = cast(_T_Ring, 0)
    for a, b in zip(vec_a, vec_b):
        ans += a * b
    return ans


class Matrix(Generic[_T_Ring]):
    # @overload
    # def __init__(self, *data: Sequence[_T_Ring], num_type: None = None) -> None: ...
    # @overload
    # def __init__(
    #     self, *data: Sequence[_T_In], num_type: Callable[[_T_In], _T_Ring]
    # ) -> None: ...

    def __init__(
        self, *data: Sequence[Any], num_type: Callable[[Any], _T_Ring] | None = None
    ) -> None:
        self.num_type = num_type or (
            type(data[0][0])
            if CONFIG["num_type"]["missing"] == "infer"
            else cast(Callable[[Any], _T_Ring], CONFIG["num_type"]["default"])
        )
        self._data = tuple(tuple(self.num_type(item) for item in row) for row in data)
        self.rows = len(data)
        self.cols = len(data[0])

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
                return (
                    "\\begin{pmatrix}"
                    + "\\\\".join("&".join(str(i) for i in row) for row in self._data)
                    + "\\end{pmatrix}"
                )

    def __getitem__(self, pos: tuple):
        row, col = pos
        return self._data[row][col]

    # TODO: row and col should be generators
    def row(self, i: int) -> Vector[_T_Ring]:
        return Vector(*self._data[i], num_type=self.num_type)

    def col(self, j: int) -> Vector[_T_Ring]:
        return Vector(
            *(self._data[i][j] for i in range(self.rows)), num_type=self.num_type
        )

    def _add(self, other: "Matrix[_T_Ring]") -> "Matrix[_T_Ring]":
        return Matrix(
            *(
                tuple(a + b for a, b in zip(row_self, row_other))
                for row_self, row_other in zip(self._data, other._data)
            ),
        )

    __add__, __radd__ = _add, _add

    @staticmethod
    def _sub(a: "Matrix[_T_Ring]", b: "Matrix[_T_Ring]") -> "Matrix[_T_Ring]":
        return Matrix(
            *(
                tuple(a - b for a, b in zip(row_a, row_b))
                for row_a, row_b in zip(a._data, b._data)
            ),
            num_type=a.num_type,
        )

    def __sub__(self: "Matrix[_T_Ring]", other: "Matrix[_T_Ring]") -> "Matrix[_T_Ring]":
        return Matrix._sub(self, other)

    def __rsub__(
        self: "Matrix[_T_Ring]", other: "Matrix[_T_Ring]"
    ) -> "Matrix[_T_Ring]":
        return Matrix._sub(other, self)

    def _mul(self, num: _T_Ring):
        return Matrix(
            *([num * item for item in row] for row in self._data),
            num_type=self.num_type,
        )

    __mul__, __rmul__ = _mul, _mul

    @staticmethod
    def _matmul(a: "Matrix[_T_Ring]", b: "Matrix[_T_Ring]") -> "Matrix[_T_Ring]":
        # TODO: DFT mat mul just because
        if a.cols != b.rows:
            raise ValueError

        return Matrix(
            *[[dot(a.row(i), b.col(j)) for j in range(b.cols)] for i in range(a.rows)],
            num_type=a.num_type,
        )

    def __matmul__(
        self: "Matrix[_T_Ring]", other: "Matrix[_T_Ring]"
    ) -> "Matrix[_T_Ring]":
        return Matrix._matmul(self, other)

    def __rmatmul__(
        self: "Matrix[_T_Ring]", other: "Matrix[_T_Ring]"
    ) -> "Matrix[_T_Ring]":
        return Matrix._matmul(other, self)

    # * small note for above
    # i dont like how some of the private methods are static but others arent
    # ideally all of them would be static, but the non static ones have their
    # own benefits

    @staticmethod
    def ident(
        size: int,
        num_type: Callable[[int], _T_RingStatic] = CONFIG["num_type"]["default"],
    ) -> "Matrix[_T_RingStatic]":
        data = tuple(tuple(int(i == j) for j in range(size)) for i in range(size))
        return Matrix(*data, num_type=num_type)

    @overload
    def __pow__(
        self: "Matrix[_T_Ring]", value: Literal["T"] | int
    ) -> "Matrix[_T_Ring]": ...
    @overload
    def __pow__(
        self: "Matrix[_T_Field]", value: Literal["T"] | int
    ) -> "Matrix[_T_Field]": ...

    def __pow__(self, value: Literal["T"] | int):
        if value == "T":
            return Matrix(
                *(
                    [self._data[j][i] for j in range(self.rows)]
                    for i in range(self.cols)
                ),
                num_type=self.num_type,
            )
        if isinstance(value, int):
            if self.rows != self.cols:
                raise ValueError

            # TODO: something like this instead of cast
            # assert isinstance(self.num_type, Callable[[int], _T_Field])
            num_type = self.num_type

            if value == 0:
                return Matrix.ident(self.rows, num_type=num_type)
            if value < 0:
                if self.rows != self.cols:
                    raise ValueError

                from .gaussian_elim import to_rref

                ops = to_rref(cast("Matrix[Field]", self), allow_zeroes=False)[1]
                inv: "Matrix[Field]" = Matrix.ident(self.rows, num_type)
                for op in ops:
                    inv = op.apply(inv)
                return inv ** abs(value)
            # return self @ (self ** (value - 1))
            return cast("Matrix[Ring]", self) @ cast("Matrix[Ring]", self)

        return NotImplemented

    def null(self: "Matrix[_T_Field]") -> tuple[Vector[_T_Field], ...]:
        from .gaussian_elim import to_rref

        mat = to_rref(self)[0]
        params = {}
        pivots = {}
        for i in range(mat.rows):
            for j in range(mat.cols):
                if mat[i, j] == mat.num_type(1):
                    pivots[j] = i
                    break
        for j in range(mat.cols):
            if j not in pivots:
                params.setdefault(j, [mat.num_type(0)] * mat.cols)[j] = mat.num_type(1)
            else:
                for j_ in range(j + 1, mat.cols):
                    if mat[pivots[j], j_] != mat.num_type(0):
                        params.setdefault(j_, [mat.num_type(0)] * mat.cols)[j] = -mat[
                            pivots[j], j_
                        ]
        return tuple(Vector(*params[k], num_type=mat.num_type) for k in params)

    def det(self: "Matrix[_T_Field]") -> _T_Field:
        """
        Note: Assumes ring is commutative
        """
        if self.rows != self.cols:
            raise ValueError

        from .mat_ops import RowSwap, RowAdd

        mat = self
        ans = self.num_type(1)

        for i in range(mat.cols):
            if mat[i, i] == self.num_type(0):
                for r in range(i, mat.rows):
                    if mat[r, i] != self.num_type(0):
                        op = RowSwap(i, r)
                        mat = op.apply(mat)
                        ans *= self.num_type(-1)
                        break
                else:
                    return self.num_type(0)

            ans *= mat[i, i]

            for r in range(i + 1, mat.rows):
                s = -mat[r, i] / mat[i, i]
                if s == self.num_type(0):
                    continue
                op = RowAdd(r, s, i)
                mat = op.apply(mat)

        return ans

    def diagonalise(
        self: "Matrix[_T_Field]",
    ) -> tuple["Matrix[_T_Field]", "Matrix[_T_Field]"]:
        """
        returns (D, P)
        """
        if self.rows != self.cols:
            raise ValueError

        def S(x) -> FieldSymbol[_T_Field]:
            return FieldSymbol(x, self.num_type)

        A = Matrix(*self._data, num_type=S)

        poly = (A - S("t") * Matrix.ident(self.rows, S)).det()

        roots: dict[_T_Field, int] = {}
        for root in single_roots(poly):
            roots[root] = roots.get(root, 0) + 1

        _D = []
        _P = []
        for root, count in roots.items():
            null = (self - root * Matrix.ident(self.rows, self.num_type)).null()
            if len(null) != count:
                raise ValueError
            _P.extend(null)
            _D.extend([root] * count)

        data = tuple(
            tuple(_D[i] if i == j else 0 for j in range(self.rows))
            for i in range(self.rows)
        )

        # print(D,P)
        return (
            Matrix(*_P, num_type=self.num_type) ** T,
            Matrix(*data, num_type=self.num_type),
        )


T = "T"

__all__ = ["Vector", "Matrix", "T", "dot"]
