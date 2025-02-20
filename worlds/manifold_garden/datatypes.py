from enum import Enum, IntFlag, auto
from typing import NamedTuple


class ConnectionType(Enum):
    SMALL = 1
    BIG = 2
    NO_SHUFFLE = 3


class GravityDirection(IntFlag):
    BLUE = auto()
    RED = auto()
    GREEN = auto()
    YELLOW = auto()
    PURPLE = auto()
    ORANGE = auto()

    def opposite(self):
        if self == GravityDirection.BLUE:
            return GravityDirection.RED
        elif self == GravityDirection.RED:
            return GravityDirection.BLUE
        elif self == GravityDirection.GREEN:
            return GravityDirection.YELLOW
        elif self == GravityDirection.YELLOW:
            return GravityDirection.GREEN
        elif self == GravityDirection.PURPLE:
            return GravityDirection.ORANGE
        elif self == GravityDirection.ORANGE:
            return GravityDirection.PURPLE


class CubeType(Enum):
    NORMAL = 1
    DARK = 2
    GOD = 3


class CubeRequirement(NamedTuple):
    color: GravityDirection
    cube_type: CubeType
    amount: int
    from_connections: tuple[str]


class Requirements:
    items: list[str]
    cubes: list[CubeRequirement]
    rooms: list[str]

    def __init__(self):
        self.items = []
        self.cubes = []
        self.rooms = []

    def has_cube_requirements(self) -> bool:
        return len(self.cubes) > 0

    def has_single_cube_requirements(self) -> bool:
        return any(cube_req.color in list(GravityDirection) for cube_req in self.cubes)

    def has_double_cube_requirements(self) -> bool:
        return any(cube_req.color not in list(GravityDirection) for cube_req in self.cubes)

    def has_item_requirements(self) -> bool:
        return len(self.items) > 0

    def has_room_requirements(self) -> bool:
        return len(self.rooms) > 0


def merge_requirements(lhs: Requirements | None, rhs: Requirements | None) -> Requirements | None:
    items = []
    cubes = []
    rooms = []

    if lhs is not None:
        if lhs.has_item_requirements():
            items += lhs.items

        if lhs.has_cube_requirements():
            cubes += lhs.cubes

        if lhs.has_room_requirements():
            rooms += lhs.rooms

    if rhs is not None:
        if rhs.has_item_requirements():
            items += rhs.items

        if rhs.has_cube_requirements():
            cubes += rhs.cubes

        if rhs.has_room_requirements():
            rooms += rhs.rooms

    if len(items) == 0 and len(cubes) == 0 and len(rooms) == 0:
        return None

    new_req = Requirements()
    new_req.items = list(set(items))
    new_req.cubes = list(set(cubes))
    new_req.rooms = list(set(rooms))

    return new_req


class Connection:
    destination: str
    pair: str
    type: ConnectionType
    plane: GravityDirection
    requirements: Requirements | None
    one_way: bool

    def __str__(self):
        return f"Connection(dest={self.destination or 'NONE'}, pair={self.pair or 'NONE'}," \
               f" type={self.type or 'NONE'}, plane={self.plane or 'NONE'})"


class TreeInfo:
    color: GravityDirection
    cube_type: CubeType
    amount: int
    to_connections: list[str]
    requirements: Requirements | None


class LocationInfo:
    name: str
    requirements: Requirements | None


class Room:
    connections: dict[str, Connection]
    trees: list[TreeInfo]
    locations: list[LocationInfo]
    transit: dict[str, dict[str, GravityDirection]]


class ManifoldGardenStaticLogic:
    rooms: dict[str, Room]
    locations: dict[str, int]
    items: dict[str, int]
