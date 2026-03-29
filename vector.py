from typing import TypeVar, Generic, Sequence, Callable, Any, cast, overload
from .number_system import *
from .config import CONFIG

_T_Ring = TypeVar("_T_Ring", bound=Ring)
_T_Field = TypeVar("_T_Field", bound=Field)


class Vector(Generic[_T_Ring], Sequence):
    def __init__(
        self, *data: Any, num_type: Callable[[Any], _T_Ring] | None = None
    ) -> None:
        self.num_type: Callable[[Any], _T_Ring] = num_type or (
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

    def _mul(self, other: _T_Ring | int | float) -> "Vector[_T_Ring]":
        other = self.num_type(other)
        return Vector(*(item * other for item in self._data), num_type=self.num_type)

    __mul__, __rmul__ = _mul, _mul

    def __truediv__(
        self: "Vector[_T_Field]", other: _T_Field | int | float
    ) -> "Vector[_T_Field]":
        other = self.num_type(other)
        return Vector(*(item / other for item in self._data), num_type=self.num_type)

    @staticmethod
    @overload
    def zero(dim: int, num_type: Callable[[Any], _T_Ring]): ...

    @staticmethod
    @overload
    def zero(vec: "Vector[_T_Ring]"): ...

    @staticmethod
    def zero(*args, **kwargs):
        if len(args) == 1 or "vec" in kwargs:
            vec = kwargs.get("vec", None) or args[0]
            dim = len(vec)
            num_type = vec.num_type
        elif len(args) == 2 or ("dim" in kwargs and "num_type" in kwargs):
            dim = kwargs.get("dim", None) or args[0]
            num_type = kwargs.get("num_type", None) or args[1]
        else:
            raise TypeError
        return Vector(*(0,) * dim, num_type=num_type)
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value,Vector):
            # TODO: check return type
            return self.num_type == value.num_type and self._data==value._data
        return NotImplemented


def dot(vec_a: Vector[_T_Ring], vec_b: Vector[_T_Ring]) -> _T_Ring:
    if len(vec_a) != len(vec_b):
        raise ValueError

    ans: _T_Ring = cast(_T_Ring, 0)
    for a, b in zip(vec_a, vec_b):
        ans += a * b
    return ans


# TODO: bad name
def coordinate(
    vec: Vector[_T_Field],
    basis: tuple[Vector[_T_Field], ...],
    prod: Callable[[Vector[_T_Field], Vector[_T_Field]], _T_Field],
) -> tuple[_T_Field, ...]:
    # TODO: check for valid basis, valid prod

    return tuple(prod(vec, bi) / prod(bi, bi) for bi in basis)


def orthogonalise(
    vecs: tuple[Vector[_T_Field], ...],
    prod: Callable[[Vector[_T_Field], Vector[_T_Field]], _T_Field],
) -> tuple[Vector[_T_Field], ...]:
    u: list[Vector[_T_Field]] = [vecs[0]]
    for i in range(1, len(vecs)):
        ui=vecs[i]-sum(
            (prod(vecs[i], u[j]) / prod(u[j], u[j]) * u[j] for j in range(len(u))),
            start=Vector.zero(vecs[0]),
        )
        if ui!=Vector.zero(vecs[0]):
            u.append(ui)
    return tuple(u)
