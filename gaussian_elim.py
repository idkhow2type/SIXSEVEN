from typing import TypeVar
from .number_system import Field
from .matrix import Matrix
from .mat_ops import *

_T_Field = TypeVar("_T_Field", bound=Field)


def to_rref(
    mat: Matrix[_T_Field], allow_zeroes=True
) -> tuple[Matrix[_T_Field], list[RowOperation[_T_Field]]]:
    ops = []

    c = 0
    for r in range(min(mat.rows, mat.cols)):
        if mat[r, c] == 0:
            for r_ in range(r, mat.rows):
                if mat[r_, r] != 0:
                    op = RowSwap(r, r_)
                    mat = op.apply(mat)
                    ops.append(op)
                    break
            else:
                try:
                    while mat[r, c] == 0:
                        c += 1
                except:
                    if allow_zeroes:
                        continue
                    else:
                        raise ValueError

        inv = 1 / mat[r, c]
        if inv != 1:
            op = RowMul(inv, r)
            mat = op.apply(mat)
            ops.append(op)

        for i0 in range(mat.rows):
            if i0 == r:
                continue
            if -mat[i0, c] == 0:
                continue
            op = RowAdd(i0, -mat[i0, c], r)
            mat = op.apply(mat)
            ops.append(op)

        c += 1

    return (mat, ops)


__all__ = ["to_rref"]
