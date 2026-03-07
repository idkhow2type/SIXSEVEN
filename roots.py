from .number_system import *


def single_roots(fn: Symbol):
    """
    finds roots of single variable function
    """
    var = fn.get_vars().pop()
    # should probably be more consistent on lists vs tuples for this kind of thing
    roots = []

    if isinstance(fn, FieldSymbol):
        if isinstance(fn.num_type, type) and issubclass(fn.num_type, Zmod):
            assert fn.num_type.base
            for x in range(fn.num_type.base):
                value = fn.evaluate({var: x})
                if value == fn.num_type(0):
                    roots.append(x)
            return roots

    raise NotImplementedError