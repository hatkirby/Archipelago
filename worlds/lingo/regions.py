from BaseClasses import MultiWorld, Region, Entrance
from .static_logic import StaticLingoLogic, Room, RoomEntrance
from .locations import LingoLocation
from .player_logic import LingoPlayerLogic
from .Options import get_option_value


def create_region(room: Room, world: MultiWorld, player: int, player_logic: LingoPlayerLogic):
    new_region = Region(room.name, player, world)

    if room.name in player_logic.LOCATIONS_BY_ROOM.keys():
        for location in player_logic.LOCATIONS_BY_ROOM[room.name]:
            new_loc = LingoLocation(player, location.name, location.code, new_region)
            new_region.locations.append(new_loc)

    world.regions += [
        new_region
    ]


def connect(target: Room, entrance: RoomEntrance, world: MultiWorld, player: int, player_logic: LingoPlayerLogic):
    target_region = world.get_region(target.name, player)
    source_region = world.get_region(entrance.room, player)
    connection = Entrance(player, f"{entrance.room} to {target.name}", source_region)
    connection.access_rule = lambda state: state.lingo_can_use_entrance(
        target.name, entrance.door, world, player, player_logic)

    source_region.exits.append(connection)
    connection.connect(target_region)


def handle_pilgrim_room(world: MultiWorld, player: int, player_logic: LingoPlayerLogic):
    target_region = world.get_region("Pilgrim Antechamber", player)
    source_region = world.get_region("Outside The Agreeable", player)
    connection = Entrance(player, f"Pilgrimage", source_region)
    connection.access_rule = lambda state: state.lingo_can_use_pilgrimage(
        player, player_logic)

    source_region.exits.append(connection)
    connection.connect(target_region)


def connect_painting(warp_enter: str, warp_exit: str, world: MultiWorld, player: int, static_logic: StaticLingoLogic,
                     player_logic: LingoPlayerLogic):
    source_painting = static_logic.PAINTINGS[warp_enter]
    target_painting = static_logic.PAINTINGS[warp_exit]

    target_region = world.get_region(target_painting.room, player)
    source_region = world.get_region(source_painting.room, player)
    connection = Entrance(player, f"{source_painting.room} to {target_painting.room} (Painting)", source_region)
    connection.access_rule = lambda state: state.lingo_can_use_entrance(
        target_painting.room, source_painting.required_door, world, player, player_logic)

    source_region.exits.append(connection)
    connection.connect(target_region)


def create_regions(world: MultiWorld, player: int, static_logic: StaticLingoLogic, player_logic: LingoPlayerLogic):
    world.regions += [
        Region("Menu", player, world)
    ]

    for room in static_logic.ALL_ROOMS:
        create_region(room, world, player, player_logic)

    for room in static_logic.ALL_ROOMS:
        for entrance in room.entrances:
            if entrance.painting and get_option_value(world, player, "shuffle_paintings"):
                # Don't use the vanilla painting connections if we are shuffling paintings.
                continue

            connect(room, entrance, world, player, player_logic)

    handle_pilgrim_room(world, player, player_logic)

    if get_option_value(world, player, "shuffle_paintings"):
        for warp_enter, warp_exit in player_logic.PAINTING_MAPPING.items():
            connect_painting(warp_enter, warp_exit, world, player, static_logic, player_logic)