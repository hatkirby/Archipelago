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
    weighting: Optional[List["OptionValue"]]

    range_random_type: Optional[RandomValueType]
    range_subset: Optional[Tuple[int, int]]

    error: Optional[str]

    def __init__(self):
        self.random = False
        self.error = None


def get_random_option_value_from_string(value: str) -> OptionValue:
    result = OptionValue()

    parts = value.split("-")
    it = 0

    if parts[it] == "random":
        result.random = True
        result.range_random_type = RandomValueType.UNIFORM
        result.weighting = None

        it += 1

    if it == len(parts):
        return result

    is_range = False
    if parts[it] == "range":
        is_range = True

        it += 1

        # It's an error for there to be no parts after "range".
        if it == len(parts):
            result.error = f"Ranged random specifier \"{value}\" missing min and max values."
            return result

    if parts[it] in ["low", "middle", "high"]:
        if parts[it] == "low":
            result.range_random_type = RandomValueType.LOW
        elif parts[it] == "middle":
            result.range_random_type = RandomValueType.MIDDLE
        elif parts[it] == "high":
            result.range_random_type = RandomValueType.HIGH

        it += 1

    if is_range:
        if it == len(parts):
            result.error = f"Ranged random specifier \"{value}\" missing min and max values."
            return result

        if it + 1 == len(parts):
            result.error = f"Ranged random specifier \"{value}\" missing max value."
            return result

        try:
            min_value = int(parts[it])
        except ValueError:
            result.error = f"Ranged random specifier \"{value}\" min value is not numeric."
            return result

        try:
            max_value = int(parts[it + 1])
        except ValueError:
            result.error = f"Ranged random specifier \"{value}\" max value is not numeric."
            return result

        result.range_subset = (min_value, max_value)

        it += 2

    if it != len(parts):
        result.error = f"Malformed random specifier \"{value}\"."

    return result


def random_option_value_to_string(ov: OptionValue) -> str:
    pass
