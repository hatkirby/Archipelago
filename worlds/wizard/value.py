from enum import Enum
from typing import Union, List, Dict, Optional, Tuple


class RandomValueType(Enum):
    UNIFORM = 1
    LOW = 2
    MIDDLE = 3
    HIGH = 4


class OptionValue:
    value: Union[str, int, List[int], Dict[int, int]]
    random: bool

    weight: int
    weighting: List["OptionValue"]

    range_random_type: Optional[RandomValueType]
    range_subset: Optional[Tuple[int, int]]

    error: Optional[str]

    def __init__(self):
        self.random = False
        self.weighting = []
        self.error = None


def get_random_option_value_from_string(value: str) -> OptionValue:
    pass
