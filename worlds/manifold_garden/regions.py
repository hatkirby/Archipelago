from typing import Callable, NamedTuple, TYPE_CHECKING

from BaseClasses import Region, Entrance, ItemClassification, CollectionState
from .datatypes import Room, merge_requirements, CubeRequirement, Requirements, GravityDirection, CubeType
from .items import ManifoldGardenItem
from .locations import ManifoldGardenLocation
from .static_logic import STATIC_LOGIC

if TYPE_CHECKING:
    from . import ManifoldGardenWorld


def _get_double_cube_room(color: GravityDirection) -> str:
    if color & (GravityDirection.BLUE | GravityDirection.RED) != 0:
        return "804"
    elif color & (GravityDirection.GREEN | GravityDirection.YELLOW) != 0:
        return "002"
    else:
        return "045_018"


def _check_requirements(state: CollectionState, world: "ManifoldGardenWorld", requirements: Requirements) -> bool:
    if requirements.items is not None:
        if not state.has_all(requirements.items, world.player):
            return False

    if requirements.cubes is not None:
        # We only handle double cube requirements in here.
        for cube_req in requirements.cubes:
            if cube_req.color in [GravityDirection.BLUE | GravityDirection.RED,
                                  GravityDirection.GREEN | GravityDirection.YELLOW,
                                  GravityDirection.PURPLE | GravityDirection.ORANGE]:
                if not state.can_reach_region(_get_double_cube_room(cube_req.color), world.player):
                    return False

    if requirements.rooms is not None:
        for room in requirements.rooms:
            if not state.can_reach_region(room, world.player):
                return False

    return True


def _check_win_condition(state: CollectionState, world: "ManifoldGardenWorld") -> bool:
    return all(state.can_reach_location(spot, world.player) for spot in ["Blue God Cube Planted",
                                                                         "Red God Cube Planted",
                                                                         "Green God Cube Planted",
                                                                         "Yellow God Cube Planted",
                                                                         "Purple God Cube Planted",
                                                                         "Orange God Cube Planted"])


def _make_req_check_lambda(world: "ManifoldGardenWorld", requirements: Requirements)\
        -> Callable[[CollectionState], bool]:
    return lambda state: _check_requirements(state, world, requirements)


def _get_door_full_requirements(room_name: str, conn_name: str) -> Requirements | None:
    room_data = STATIC_LOGIC.rooms[room_name]
    conn_data = room_data.connections[conn_name]

    paired_room = STATIC_LOGIC.rooms[conn_data.destination]
    paired_conn = paired_room.connections[conn_data.pair]

    requirements = merge_requirements(conn_data.requirements, paired_conn.requirements)

    if paired_conn.one_way:
        add_req = Requirements()
        add_req.rooms = [conn_data.destination]

        requirements = merge_requirements(requirements, add_req)

    return requirements


def _create_connection(world: "ManifoldGardenWorld", regions: dict[str, Region], source_region: Region,
                       target_region: Region, description: str | None, requirements: Requirements | None):
    connection = Entrance(world.player, description if description else f"{source_region.name} -> {target_region.name}",
                          source_region)
    connection.connect(target_region)
    source_region.exits.append(connection)

    if requirements is not None:
        connection.access_rule = _make_req_check_lambda(world, requirements)

        if requirements.has_double_cube_requirements():
            for cube_req in requirements.cubes:
                if cube_req.color not in list(GravityDirection):
                    double_cube_room = _get_double_cube_room(cube_req.color)
                    world.multiworld.register_indirect_condition(regions[double_cube_room], connection)

        if requirements.has_room_requirements():
            for room in requirements.rooms:
                world.multiworld.register_indirect_condition(regions[room], connection)


def _create_region_from_room(world: "ManifoldGardenWorld", room_name: str, room_data: Room) -> Region:
    new_region = Region(room_name, world.player, world.multiworld)
    for location in room_data.locations:
        if location.requirements is not None and location.requirements.has_single_cube_requirements():
            # We will take care of these later.
            continue

        new_location = ManifoldGardenLocation(world.player, location.name,
                                              STATIC_LOGIC.locations[location.name], new_region)

        if location.requirements is not None:
            new_location.access_rule = _make_req_check_lambda(world, location.requirements)

        new_region.locations.append(new_location)

    return new_region


# BIGGEST CURRENT TODO: prune parts of the graph that can't ever reach a tree
def _create_cube_graph(world: "ManifoldGardenWorld", req: CubeRequirement, starting_room: str,
                       regions: dict[str, Region]) -> str:
    region_name_prefix = f"{starting_room}!{req}!"

    class ConnectionInfo(NamedTuple):
        room_name: str
        room_exit: str

        def make_region_name(self):
            return f"{region_name_prefix}{self.room_name}:{self.room_exit}"

    def make_tree_region_name(room_name: str, connections: list[str]):
        return f"{region_name_prefix}{room_name}.Tree({','.join(connections)})"

    flood_edge = [ConnectionInfo(starting_room, conn) for conn in req.from_connections]
    visited = set(flood_edge)

    for connection in flood_edge:
        region_name = connection.make_region_name()
        new_region = Region(region_name, world.player, world.multiworld)
        regions[region_name] = new_region

        _create_connection(world, regions, regions[starting_room], new_region, None,
                           _get_door_full_requirements(connection.room_name, connection.room_exit))

    tree_regions = []

    while len(flood_edge) > 0:
        next_connection = flood_edge.pop(0)

        connection_region = regions[next_connection.make_region_name()]

        current_room = STATIC_LOGIC.rooms[next_connection.room_name]
        current_connection = current_room.connections[next_connection.room_exit]

        paired_room = STATIC_LOGIC.rooms[current_connection.destination]

        for tree in paired_room.trees:
            if tree.color == req.color and tree.cube_type == req.cube_type\
                    and current_connection.pair in tree.to_connections:
                tree_region_name = make_tree_region_name(current_connection.destination, tree.to_connections)
                if tree_region_name not in tree_regions:
                    new_region = Region(tree_region_name, world.player, world.multiworld)
                    regions[tree_region_name] = new_region
                    tree_regions.append(tree_region_name)

                    if req.amount > 1:
                        for i in range(tree.amount):
                            event_location = ManifoldGardenLocation(world.player, f"{tree_region_name}!{i}", None,
                                                                    new_region)
                            new_region.locations.append(event_location)
                            event_item = ManifoldGardenItem(f"{region_name_prefix}Cube",
                                                            ItemClassification.progression, None, world.player)
                            event_location.place_locked_item(event_item)

                add_reqs = Requirements()
                add_reqs.rooms = [current_connection.destination]

                tree_requirements = merge_requirements(add_reqs, tree.requirements)

                _create_connection(world, regions, connection_region, regions[tree_region_name], None,
                                   tree_requirements)

        for from_transit_name, from_transit_data in paired_room.transit.items():
            if current_connection.pair in from_transit_data and \
                    (req.color & from_transit_data[current_connection.pair]) != 0:
                following_info = ConnectionInfo(current_connection.destination, from_transit_name)
                following_region_name = following_info.make_region_name()

                if following_info not in visited:
                    new_region = Region(following_region_name, world.player, world.multiworld)
                    regions[following_region_name] = new_region

                    flood_edge.append(following_info)
                    visited.add(following_info)

                _create_connection(world, regions, connection_region, regions[following_region_name], None,
                                   _get_door_full_requirements(current_connection.destination, current_connection.pair))

    final_region_name = f"{region_name_prefix}DONE"
    final_region = Region(final_region_name, world.player, world.multiworld)
    regions[final_region_name] = final_region

    if req.amount == 1:
        for tree_region_name in tree_regions:
            regions[tree_region_name].connect(final_region)
    else:
        regions[starting_room].connect(final_region, None,
                                       lambda state: state.has(f"{region_name_prefix}Cube", world.player, req.amount))

    # Double cubes can't be used for dark cube or god cube fetch quests.
    # They also won't work for the Apartments Waterwheel check.
    if req.cube_type == CubeType.NORMAL and req.amount <= 2:
        double_cube_room = _get_double_cube_room(req.color)

        double_cube_connection = Entrance(world.player, f"{region_name_prefix}_DoubleCubeSkip", regions[starting_room])
        double_cube_connection.access_rule = lambda state: state.can_reach_region(double_cube_room, world.player)
        regions[starting_room].exits.append(double_cube_connection)
        double_cube_connection.connect(final_region)
        world.multiworld.register_indirect_condition(regions[double_cube_room], double_cube_connection)

    print(f"{region_name_prefix} hunt has {len(visited)} regions")

    return final_region_name


def create_regions(world: "ManifoldGardenWorld"):
    regions: dict[str, Region] = {"Menu": Region("Menu", world.player, world.multiworld)}

    # Create the main regions.
    for room_name, room_data in STATIC_LOGIC.rooms.items():
        regions[room_name] = _create_region_from_room(world, room_name, room_data)

    # Create the normal connections.
    for room_name, room_data in STATIC_LOGIC.rooms.items():
        for conn_name, conn_data in room_data.connections.items():
            other_conn = STATIC_LOGIC.rooms[conn_data.destination].connections[conn_data.pair]

            if other_conn.one_way:
                continue

            # We are going to ignore connections with cube requirements for now.
            _create_connection(world, regions, regions[room_name], regions[conn_data.destination],
                               f"{room_name}:{conn_name}",
                               _get_door_full_requirements(room_name, conn_name))

    # Connect the start of the game.
    regions["Menu"].connect(regions["000"])

    # Connect the end of the game.
    event_location = ManifoldGardenLocation(world.player, "Raymarchitecture", None, regions["804"])
    event_location.access_rule = lambda state: _check_win_condition(state, world)
    regions["804"].locations.append(event_location)
    event_item = ManifoldGardenItem("Victory", ItemClassification.progression, None, world.player)
    event_location.place_locked_item(event_item)

    # Set up locations with cube requirements.
    for room_name, room_data in STATIC_LOGIC.rooms.items():
        needed_cube_graphs: set[CubeRequirement] = set()

        for location in room_data.locations:
            if location.requirements is not None and location.requirements.has_single_cube_requirements():
                for req in location.requirements.cubes:
                    needed_cube_graphs.add(req)

        cube_graph_end_rooms = {req: _create_cube_graph(world, req, room_name, regions) for req in needed_cube_graphs}

        for location in room_data.locations:
            if location.requirements is not None and location.requirements.has_single_cube_requirements():
                # can't deal with multiple reqs rn lol let's just pretend it's always one
                req = location.requirements.cubes[0]
                end_room_name = cube_graph_end_rooms[req]
                end_room_region = regions[end_room_name]

                new_location = ManifoldGardenLocation(world.player, location.name,
                                                      STATIC_LOGIC.locations[location.name], end_room_region)
                new_location.access_rule = _make_req_check_lambda(world, location.requirements)
                end_room_region.locations.append(new_location)

    world.multiworld.regions += regions.values()
