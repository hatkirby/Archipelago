from typing import NamedTuple, TYPE_CHECKING

from .datatypes import CubeRequirement, ConnectionType, EntranceIdentifier, ConnectionFilter, Connection, \
    GravityDirection, CubeType
from .static_logic import STATIC_LOGIC

if TYPE_CHECKING:
    from . import ManifoldGardenWorld


def _get_possible_transports(room_name: str, to_conn: str, color: GravityDirection) -> set[str, Connection]:
    room_data = STATIC_LOGIC.rooms[room_name]
    next_exits = set()
    for next_exit_name, next_exit_data in room_data.connections.items():
        if next_exit_name == to_conn or room_data.transit.get(next_exit_name, {}).get(to_conn, 0) & color == 0:
            continue

        next_exits.add(next_exit_name)

    return next_exits


class ERConnection(NamedTuple):
    cur_room: str
    exit: str
    other_room: str
    entrance: str
    terminal: bool

    def overlaps(self, other: "ERConnection"):
        return (self.cur_room == other.cur_room and self.exit == other.exit) or\
            (self.cur_room == other.other_room and self.exit == other.entrance) or\
            (self.other_room == other.cur_room and self.entrance == other.exit) or\
            (self.other_room == other.other_room and self.entrance == other.entrance)


class ERSearchNode:
    room: str
    from_entrance: str | None
    color: GravityDirection
    cube_type: CubeType
    orig_amount: int
    from_connections: set[str]

    expanded_exits: set[EntranceIdentifier]
    possibilities: set[ERConnection]

    path: list[ERConnection]
    amount: int
    has_tree: bool
    needed_for: str

    def __init__(self, room: str, from_entrance: str | None, color: GravityDirection, cube_type: CubeType, amount: int,
                 from_connections: set[str], needed_for: str):
        self.room = room
        self.from_entrance = from_entrance

        self.color = color
        self.cube_type = cube_type
        self.orig_amount = amount
        self.amount = amount
        self.from_connections = from_connections

        self.has_tree = False
        self.path = []
        self.touched_rooms = set()
        self.needed_for = needed_for

    @classmethod
    def from_cube_req(cls, room: str, from_entrance: str | None, cube_req: CubeRequirement, needed_for: str):
        return cls(room, from_entrance, cube_req.color, cube_req.cube_type, cube_req.amount,
                   set(cube_req.from_connections), needed_for)

    def expand_region(self, er: "EntranceRandomizer"):
        self.expanded_exits = set()
        self.amount = self.orig_amount
        self.touched_rooms.add(self.room)

        room_data = STATIC_LOGIC.rooms[self.room]

        possible_exits = dict()
        for conn_name, conn_data in room_data.connections.items():
            if conn_name in self.from_connections:
                possible_exits[conn_name] = conn_data

        self._expand_region_helper(self.room, self.from_entrance, possible_exits, set(), er)

    def _expand_region_helper(self, cur_room: str, from_entrance: str | None, possible_exits: dict[str, Connection],
                              visited: set[EntranceIdentifier], er: "EntranceRandomizer"):
        if from_entrance is not None:
            room_data = STATIC_LOGIC.rooms[cur_room]

            for tree_data in room_data.trees:
                if tree_data.color == self.color and tree_data.cube_type == self.cube_type and\
                        from_entrance in tree_data.to_connections:
                    if self.amount > tree_data.amount:
                        self.amount = self.amount - tree_data.amount
                    else:
                        self.has_tree = True

        for conn_name, conn_data in possible_exits.items():
            my_iden = EntranceIdentifier(cur_room, conn_name)

            if conn_data.type == ConnectionType.NO_SHUFFLE:
                entrance = EntranceIdentifier(conn_data.destination, conn_data.pair)
            elif my_iden in er.connection_by_pair:
                entrance = er.connection_by_pair[my_iden]
            else:
                self.expanded_exits.add(EntranceIdentifier(cur_room, conn_name))
                continue

            if entrance in visited:
                continue
            else:
                visited.add(entrance)

            self.touched_rooms.add(entrance.room)
            other_room_data = STATIC_LOGIC.rooms[entrance.room]
            next_exit_names = _get_possible_transports(entrance.room, entrance.entrance, self.color)
            next_exits = {exit_name: exit_data for exit_name, exit_data in other_room_data.connections.items()
                          if exit_name in next_exit_names}

            self._expand_region_helper(entrance.room, entrance.entrance, next_exits, visited, er)

    def filter_possibilities(self, er: "EntranceRandomizer"):
        self.possibilities = set()

        for possible_exit in self.expanded_exits:
            room_data = STATIC_LOGIC.rooms[possible_exit.room]
            exit_data = room_data.connections[possible_exit.entrance]

            connection_filter = ConnectionFilter(exit_data.type, exit_data.plane.opposite())
            matched_entrances = STATIC_LOGIC.entrances.get(connection_filter, [])
            for entrance in matched_entrances:
                # TODO: it should be okay to go into the same room as long as there's another exit
                if entrance in er.used_entrances or entrance.room in self.touched_rooms:
                    continue

                possible_transports = _get_possible_transports(entrance.room, entrance.entrance, self.color)
                if len(possible_transports) == 0:
                    continue

                sub_search = ERSearchNode(entrance.room, entrance.entrance, self.color, self.cube_type, self.amount,
                                          possible_transports, self.needed_for)
                sub_search.expand_region(er)
                if not sub_search.has_tree and len(sub_search.expanded_exits) == 0:
                    continue

                new_connection = ERConnection(possible_exit.room, possible_exit.entrance, entrance.room,
                                              entrance.entrance, sub_search.has_tree)
                self.possibilities.add(new_connection)

    def prune_possible_connection(self, connection: ERConnection, er: "EntranceRandomizer"):
        if any(p.overlaps(connection) for p in self.possibilities):
            self.expand_region(er)
            self.filter_possibilities(er)


class ERRegion:
    available_exits: set[str]
    connections: dict[str, EntranceIdentifier]

    def __init__(self, name: str):
        self.available_exits = set()
        self.connections = {}

        room_data = STATIC_LOGIC.rooms[name]
        for conn_name, conn_data in room_data.connections.items():
            if conn_data.type == ConnectionType.NO_SHUFFLE:
                self.connections[conn_name] = EntranceIdentifier(conn_data.destination, conn_data.pair)
            else:
                self.available_exits.add(conn_name)

    def is_finished(self) -> bool:
        return len(self.available_exits) == 0

    def is_dead_end(self) -> bool:
        return len(self.available_exits) == 1

    def connect(self, exit_name: str, other_room: str, entrance_name: str):
        self.available_exits.remove(exit_name)
        self.connections[exit_name] = EntranceIdentifier(other_room, entrance_name)


class EntranceRandomizer:
    world: "ManifoldGardenWorld"

    search_nodes: list[ERSearchNode]
    used_entrances: set[EntranceIdentifier]
    connections: list[ERConnection]
    connection_by_pair: dict[EntranceIdentifier, EntranceIdentifier]
    touched_rooms: set[str]

    reachable_regions: set[str]
    regions: dict[str, ERRegion]
    dead_ends: dict[EntranceIdentifier, bool]

    def __init__(self, world: "ManifoldGardenWorld"):
        self.world = world
        self.search_nodes = []
        self.used_entrances = set()
        self.connections = []
        self.connection_by_pair = {}
        self.touched_rooms = set()
        self.reachable_regions = set()
        self.regions = {}
        self.dead_ends = {}

        for room_name in STATIC_LOGIC.rooms.keys():
            self.regions[room_name] = ERRegion(room_name)

    def randomize(self):
        if self.world.options.apartments_waterwheel_puzzle.value:
            self._connect(ERConnection("045", "F", "045_073", "A", False))

        # Ensure that cube carrying paths exist.
        self._find_puzzle_nodes()
        self._create_paths()

        # Connect the rest of the world.
        self._sweep_reachable_regions("000")

        while self._find_and_make_connection(dead_end=False, untouched=True):
            pass

        while self._find_and_make_connection(dead_end=True, untouched=True):
            pass

        while self._find_and_make_connection(dead_end=True, untouched=False):
            pass

        while self._find_and_make_connection(dead_end=False, untouched=False):
            pass

        print("Sanity checking regions:")
        for region_name in STATIC_LOGIC.rooms.keys():
            if region_name not in self.reachable_regions:
                print(f"    {region_name} is not reachable")

        for region_name, region_data in self.regions.items():
            if not region_data.is_finished():
                print(f"    {region_name} is not finished ({region_data.available_exits})")

    def _find_puzzle_nodes(self):
        for room_name, room_data in STATIC_LOGIC.rooms.items():
            for conn_name, conn_data in room_data.connections.items():
                if conn_data.requirements is not None:
                    for cube_req in conn_data.requirements.cubes:
                        if not cube_req.color.is_single():
                            continue

                        node = ERSearchNode.from_cube_req(room_name, None, cube_req, f"{room_name} exit {conn_name}")

                        if conn_name in node.from_connections:
                            node.from_connections.remove(conn_name)

                        self.search_nodes.append(node)

            for tree_data in room_data.trees:
                if tree_data.requirements is not None:
                    for cube_req in tree_data.requirements.cubes:
                        self.search_nodes.append(ERSearchNode.from_cube_req(room_name, None, cube_req,
                                                                            f"{room_name} tree {tree_data.color}"))

            for loc_data in room_data.locations:
                if loc_data.name == "Apartments Waterwheel Activated" and\
                        not self.world.options.apartments_waterwheel_puzzle.value:
                    continue

                if loc_data.requirements is not None:
                    for cube_req in loc_data.requirements.cubes:
                        self.search_nodes.append(ERSearchNode.from_cube_req(room_name, None, cube_req, loc_data.name))

        for search_node in self.search_nodes:
            search_node.expand_region(self)

            if not search_node.has_tree:
                search_node.filter_possibilities(self)

        self.search_nodes = [sn for sn in self.search_nodes if not sn.has_tree]

    def _create_paths(self):
        self.world.random.shuffle(self.search_nodes)

        while len(self.search_nodes) > 0:
            next_node: ERSearchNode = min(self.search_nodes, key=lambda sn: len(sn.possibilities))
            self.search_nodes.remove(next_node)

            if next_node.has_tree:
                continue

            if len(next_node.possibilities) == 0:
                raise Exception(f"No possibilities for room {next_node.room} connections {next_node.expanded_exits}")

            # Prioritize ending the path if we're over the length
            possibilities = list(next_node.possibilities)
            terminal_possibilities = [p for p in possibilities if p.terminal]

            if len(next_node.path) >= 5 and len(terminal_possibilities) > 0:
                possibilities = terminal_possibilities
            else:
                # Try to connect to an untouched room.
                untouched_possibilities = [p for p in possibilities if p.other_room not in self.touched_rooms]
                if len(untouched_possibilities) > 0:
                    possibilities = untouched_possibilities

            chosen_possibility: ERConnection = self.world.random.choice(possibilities)
            print(f"Connecting {chosen_possibility}: needed for {next_node.needed_for}")

            self._connect(chosen_possibility)

            for touched_room in next_node.touched_rooms:
                self.touched_rooms.add(touched_room)

            for existing_node in self.search_nodes:
                existing_node.prune_possible_connection(chosen_possibility, self)

            if not chosen_possibility.terminal:
                added_node = ERSearchNode(chosen_possibility.other_room, chosen_possibility.entrance, next_node.color,
                                          next_node.cube_type, next_node.amount,
                                          _get_possible_transports(chosen_possibility.other_room,
                                                                   chosen_possibility.entrance, next_node.color),
                                          next_node.needed_for)
                added_node.path = next_node.path.copy()
                added_node.path.append(chosen_possibility)

                if chosen_possibility.entrance in added_node.from_connections:
                    added_node.from_connections.remove(chosen_possibility.entrance)

                added_node.expand_region(self)
                added_node.filter_possibilities(self)

                self.search_nodes.append(added_node)

    def _connect(self, connection: ERConnection):
        self.connections.append(connection)
        self.used_entrances.add(EntranceIdentifier(connection.cur_room, connection.exit))
        self.used_entrances.add(EntranceIdentifier(connection.other_room, connection.entrance))

        exit_iden = EntranceIdentifier(connection.cur_room, connection.exit)
        enter_iden = EntranceIdentifier(connection.other_room, connection.entrance)
        self.connection_by_pair[exit_iden] = enter_iden
        self.connection_by_pair[enter_iden] = exit_iden

        self.regions[connection.cur_room].connect(connection.exit, connection.other_room, connection.entrance)
        self.regions[connection.other_room].connect(connection.entrance, connection.cur_room, connection.exit)

        if connection.cur_room in self.reachable_regions:
            self._sweep_reachable_regions(connection.cur_room)

        if connection.other_room in self.reachable_regions:
            self._sweep_reachable_regions(connection.other_room)

    def _sweep_reachable_regions(self, from_region: str):
        boundary: list[str] = [from_region]

        while len(boundary) > 0:
            cur_room = boundary.pop()
            self.reachable_regions.add(cur_room)

            region = self.regions[cur_room]
            for exit_name, entrance in region.connections.items():
                if entrance.room not in self.reachable_regions:
                    boundary.append(entrance.room)

    def _is_entrance_dead_end(self, entrance: EntranceIdentifier) -> bool:
        if entrance in self.dead_ends:
            return self.dead_ends[entrance]

        boundary = [entrance]
        exits = set()
        visited = set()

        while len(boundary) > 0:
            next_entrance = boundary.pop()
            visited.add(next_entrance.room)
            room_data = STATIC_LOGIC.rooms[next_entrance.room]

            for conn_name, conn_data in room_data.connections.items():
                if conn_name == next_entrance.entrance:
                    continue

                if conn_data.type == ConnectionType.NO_SHUFFLE:
                    if conn_data.destination not in visited:
                        boundary.append(EntranceIdentifier(conn_data.destination, conn_data.pair))
                elif EntranceIdentifier(next_entrance.room, conn_name) in self.used_entrances:
                    if self.regions[next_entrance.room].connections[conn_name].room not in visited:
                        boundary.append(self.regions[next_entrance.room].connections[conn_name])
                else:
                    exits.add(EntranceIdentifier(next_entrance.room, conn_name))

        is_dead_end = (len(exits) == 1)
        self.dead_ends[entrance] = is_dead_end
        return is_dead_end

    def _find_and_make_connection(self, dead_end: bool, untouched: bool) -> bool:
        reachable_exits: list[EntranceIdentifier] = []

        for region_name in self.reachable_regions:
            for exit_name in self.regions[region_name].available_exits:
                reachable_exits.append(EntranceIdentifier(region_name, exit_name))

        self.world.random.shuffle(reachable_exits)

        for source_exit in reachable_exits:
            room_data = STATIC_LOGIC.rooms[source_exit.room]
            conn_data = room_data.connections[source_exit.entrance]

            connection_filter = ConnectionFilter(conn_data.type, conn_data.plane.opposite())
            matched_entrances = STATIC_LOGIC.entrances.get(connection_filter, [])
            usable_entrances = [entrance for entrance in matched_entrances if entrance not in self.used_entrances]

            if len(usable_entrances) == 0:
                # this is honestly not good tho
                print(f"{source_exit} has no usable pairs")
                continue

            self.world.random.shuffle(usable_entrances)

            for entrance in usable_entrances:
                if (entrance.room not in self.reachable_regions) != untouched:
                    continue

                if self._is_entrance_dead_end(entrance) != dead_end:
                    continue

                print(f"Connecting {source_exit} -> {entrance} (dead_end={dead_end}, untouched={untouched})")

                self._connect(ERConnection(source_exit.room, source_exit.entrance, entrance.room, entrance.entrance,
                                           terminal=False))
                return True

        return False
