from .matrix import Matrix, T
from typing import Literal, cast

Permutation = tuple[int, ...]


# this is a disgusting way to write it
# but it respects the data model so thats cool
def permute(f: Permutation, mat: Matrix):
    return Matrix(*[mat.col(f[i]) for i in range(len(f))]) ** T


def sign(f: Permutation) -> Literal[-1, 1]:
    ans = 1
    _f = list(f)
    for i in range(len(_f)):
        m = i
        for j in range(i, len(_f)):
            if _f[j] < _f[m]:
                m = j
        if m != i:
            _f[m], _f[i] = _f[i], _f[m]
            ans *= -1
    return cast(Literal[1, -1], ans)

def leibniz_term(f: Permutation, mat: Matrix):
    ans=sign(f)
    for i in range(len(f)):
        ans*=mat[f[i],i]
    return ans

__all__ = ["permute", "sign", "Permutation","leibniz_term"]
