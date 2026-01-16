from typing import TypedDict, Literal


class Config(TypedDict):
    repr_type: Literal["default", "latex"]


CONFIG: Config = {"repr_type": "default"}
