# SIXSEVEN

<small>**S**<sub>ymbolic</sub>
**I**<sub>nterface for</sub>
**X**<sub>-dimensional</sub>
**S**<sub>ystems,</sub>
**E**<sub>quations,</sub>
**V**<sub>ectors, and</sub>
**E**<sub>igen-</sub>
**N**<sub>etworks.</sub></small>

---

A terrible linear algebra and symbolic math system, the result of an off-handed comment by a linear algebra professor and absolute insistence on not manually doing homework.

## Featuring:
- Crazy static type safety
- Structural typing for different number systems (fields, rings, ...)
- Flexible matrices and vectors, supporting any* valid number system
- Symbolic arithmetic system for any* valid number system
- Almost no functional dependency (most dependencies are from the type system)

<small>*Well that's the plan at least, we'll see where it goes</small>

## Example(s):
```python
from lib import *

def S(n):
    return FieldSymbol(n, Fraction)

mat = Matrix(
    ("A" , 1 , -1) ,
    ("B" , 4 , 0 ) ,
    ("C" , 1 , 2 ),
    num_type=S
)

print(mat.det()) # this is the correct deteminant trust
```

## TODOS:

- [ ] `matrix.rank()`
- [x] Symbol number type
- [ ] Matrix needs to properly support commutative rings
    - [ ] Matrix methods use `self.num_type(0)` and `self.num_type(1)` for add and mult identity, make that part of number system
    - [ ] `det` and inverse uses division, replace with the fancy algorithm
- [ ] Maybe eigenvalue definition of sqrt of matrix
- [ ] ~~Change `Callable[[Any],T]` to `type[T]`~~ This seems too complicated, the other way gets the idea across
- [x] Unary `-`/`+`
- [ ] Replace `__init__` with `__new__` (maybe but probably not)
- [ ] Implement equal for Matrix and Vector
- [x] Symbol support for ops with `int` and `float`
- [ ] Refactor `Zmod` to bind pattern
- [ ] Implement default `num_type` for `FieldSymbol` or rework that system entirely
- [ ] Split up files and make some folders
- [x] Update unit tests
- [ ] Rewrite the entire add and mult term grouping again
    - No more sorting as preprocessing, really expensive and doesn't work that well
    - Still need sorting for display mostly, so who knows?