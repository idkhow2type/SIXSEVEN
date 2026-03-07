from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from .number_system.num_types import Field
from .matrix import Matrix

_T_Field = TypeVar("_T_Field", bound=Field)


class RowOperation(ABC, Generic[_T_Field]):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def apply(self, mat: Matrix[_T_Field]) -> Matrix[_T_Field]:
        pass


class RowAdd(RowOperation[_T_Field]):
    def __init__(self, dest: int, scale: _T_Field, src: int) -> None:
        super().__init__()
        self.dest = dest
        self.src = src
        self.scale = scale

    def apply(self, mat):
        # * This is repetitive, but the alterantive is probably more ridiculous
        # TODO: respect private _data, use official row() getter
        data = [list(row) for row in mat._data]
        data[self.dest] = list(mat.row(self.dest) + self.scale * mat.row(self.src))
        return Matrix(*data,num_type=mat.num_type)

    def __repr__(self) -> str:
        return f"R{self.dest} -> R{self.dest} + {self.scale}*R{self.src}"


class RowMul(RowOperation[_T_Field]):
    def __init__(self, scale: _T_Field, row: int) -> None:
        super().__init__()
        self.scale = scale
        self.row = row

    def apply(self, mat):
        data = [list(row) for row in mat._data]
        data[self.row] = list(self.scale * mat.row(self.row))
        return Matrix(*data,num_type=mat.num_type)

    def __repr__(self) -> str:
        return f"R{self.row} -> {self.scale}*R{self.row}"


class RowSwap(RowOperation[_T_Field]):
    def __init__(self, row_a: int, row_b: int) -> None:
        super().__init__()
        self.row_a = row_a
        self.row_b = row_b

    def apply(self, mat):
        data = [list(row) for row in mat._data]
        data[self.row_a], data[self.row_b] = data[self.row_b], data[self.row_a]
        return Matrix(*data,num_type=mat.num_type)

    def __repr__(self) -> str:
        return f"R{self.row_a} <-> R{self.row_b}"


__all__ = ["RowOperation", "RowAdd", "RowMul", "RowSwap"]
