from typing import TypedDict, Literal, Callable
from .number_system.num_types import Fraction


class _num_type(TypedDict):
    missing: Literal["infer", "default"]
    default: None | Callable


class Config(TypedDict):
    repr_type: Literal["default", "latex"]
    num_type: _num_type


CONFIG: Config = {
    "repr_type": "default",
    "num_type": {"missing": "default", "default": Fraction},
}

__all__ = ["CONFIG"]
