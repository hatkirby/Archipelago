import logging
import pkgutil

import Utils
from .datatypes import ManifoldGardenStaticLogic, Room, Connection, ConnectionType, GravityDirection, Requirements, \
    CubeRequirement, CubeType, LocationInfo, TreeInfo

STATIC_LOGIC: ManifoldGardenStaticLogic


def process_gravity_direction(val) -> GravityDirection | None:
    if val == "blue":
        return GravityDirection.BLUE
    elif val == "red":
        return GravityDirection.RED
    elif val == "green":
        return GravityDirection.GREEN
    elif val == "yellow":
        return GravityDirection.YELLOW
    elif val == "purple":
        return GravityDirection.PURPLE
    elif val == "orange":
        return GravityDirection.ORANGE
    elif val == "red/blue":
        return GravityDirection.RED | GravityDirection.BLUE
    elif val == "green/yellow":
        return GravityDirection.GREEN | GravityDirection.YELLOW
    elif val == "purple/orange":
        return GravityDirection.PURPLE | GravityDirection.ORANGE
    else:
        logging.warning(f"Invalid gravity direction: {val}")
        return None


def process_cube_requirement(path, cube_data) -> CubeRequirement:
    if "color" in cube_data:
        color = process_gravity_direction(cube_data["color"])

        if color is None:
            color = GravityDirection.BLUE
            logging.warning(f"{path} cube requirement has an invalid color")
        else:
            color = color
    else:
        color = GravityDirection.BLUE
        logging.warning(f"{path} cube requirement is missing a color")

    if "god" in cube_data and cube_data["god"]:
        cube_type = CubeType.GOD
    elif "dark" in cube_data and cube_data["dark"]:
        cube_type = CubeType.DARK
    else:
        cube_type = CubeType.NORMAL

    if "amount" in cube_data:
        amount = cube_data["amount"]
    else:
        amount = 1

    if "from" in cube_data:
        from_connections = tuple(cube_data["from"])
    else:
        from_connections = ()
        logging.warning(f"{path} is missing from connections")

    return CubeRequirement(color, cube_type, amount, from_connections)


def process_requirements(path, data) -> Requirements:
    requirements = Requirements()

    if "item" in data:
        if isinstance(data["item"], list):
            requirements.items = data["item"]
        else:
            requirements.items = [data["item"]]

    if "cube_req" in data:
        if isinstance(data["cube_req"], list):
            requirements.cubes = [process_cube_requirement(path, cube_data) for cube_data in data["cube_req"]]
        else:
            requirements.cubes = [process_cube_requirement(path, data["cube_req"])]

    return requirements


def process_connection(path, conn_data) -> Connection:
    connection = Connection()

    if "dest" in conn_data:
        connection.destination = conn_data["dest"]
    else:
        logging.warning(f"{path} is missing a dest room")

    if "pair" in conn_data:
        connection.pair = conn_data["pair"]
    else:
        logging.warning(f"{path} is missing a pair")

    if "type" in conn_data:
        if conn_data["type"] == "big":
            connection.type = ConnectionType.BIG
        elif conn_data["type"] == "small":
            connection.type = ConnectionType.SMALL
        elif conn_data["type"] == "no_shuffle":
            connection.type = ConnectionType.NO_SHUFFLE
        else:
            logging.warning(f"{path} has an invalid type: {conn_data['type']}")
    else:
        logging.warning(f"{path} is missing a type")

    if "plane" in conn_data:
        plane = process_gravity_direction(conn_data["plane"])

        if plane is None:
            logging.warning(f"{path} has an invalid plane color")
        else:
            connection.plane = plane
    else:
        logging.warning(f"{path} is missing a plane")

    if "item" in conn_data or "cube_req" in conn_data:
        connection.requirements = process_requirements(path, conn_data)
    else:
        connection.requirements = None

    if "one_way" in conn_data and conn_data["one_way"]:
        connection.one_way = True
    else:
        connection.one_way = False

    return connection


def process_tree(room_name, tree_data) -> TreeInfo:
    tree = TreeInfo()

    if "color" in tree_data:
        color = process_gravity_direction(tree_data["color"])

        if color is None:
            logging.warning(f"{room_name} tree has an invalid color")
        else:
            tree.color = color
    else:
        logging.warning(f"{room_name} tree is missing a color")

    if "god" in tree_data and tree_data["god"]:
        tree.cube_type = CubeType.GOD
    elif "dark" in tree_data and tree_data["dark"]:
        tree.cube_type = CubeType.DARK
    else:
        tree.cube_type = CubeType.NORMAL

    if "amount" in tree_data:
        tree.amount = tree_data["amount"]
    else:
        tree.amount = 1

    if "to" in tree_data:
        tree.to_connections = tree_data["to"]
    else:
        logging.warning(f"{room_name} is missing to connections")

    if "item" in tree_data or "cube_req" in tree_data:
        tree.requirements = process_requirements(f"{room_name}:tree", tree_data)
    else:
        tree.requirements = None

    return tree


def process_location(room_name, loc_data) -> LocationInfo:
    location = LocationInfo()

    if isinstance(loc_data, str):
        location.name = loc_data
        location.requirements = None
    elif isinstance(loc_data, dict):
        if "name" in loc_data:
            location.name = loc_data["name"]
        else:
            logging.warning(f"{room_name} has a location without a name")

        if "item" in loc_data or "cube_req" in loc_data:
            location.requirements = process_requirements(f"{room_name}:{location.name}", loc_data)
        else:
            location.requirements = None

    return location


def process_room(room_name, room_data) -> Room:
    room = Room()
    room.connections = {}
    room.trees = []
    room.locations = []
    room.transit = {}

    if "connections" in room_data:
        for conn_name, conn_data in room_data["connections"].items():
            room.connections[conn_name] = process_connection(f"{room_name}:{conn_name}", conn_data)

    if "cubes" in room_data:
        for tree_data in room_data["cubes"]:
            room.trees.append(process_tree(room_name, tree_data))

    if "locations" in room_data:
        for loc_data in room_data["locations"]:
            room.locations.append(process_location(room_name, loc_data))

    if "transit" in room_data:
        for transit_data in room_data["transit"]:
            transit_from = transit_data["from"] if isinstance(transit_data["from"], list) else [transit_data["from"]]
            transit_to = transit_data["to"] if isinstance(transit_data["to"], list) else [transit_data["to"]]

            for f in transit_from:
                room.transit.setdefault(f, {})
                from_conn = room.transit[f]

                for t in transit_to:
                    if f == t:
                        continue

                    from_conn.setdefault(t, 0)

                    from_conn[t] = from_conn[t] | sum(process_gravity_direction(color)
                                                      for color in transit_data["colors"])

    return room


def load_static_logic():
    global STATIC_LOGIC

    STATIC_LOGIC = ManifoldGardenStaticLogic()
    STATIC_LOGIC.rooms = {}

    file = pkgutil.get_data(__name__, "data/world.yaml")
    config = Utils.parse_yaml(file)

    for room_name, room_data in config.items():
        STATIC_LOGIC.rooms[room_name] = process_room(room_name, room_data)

    for rname, rdata in STATIC_LOGIC.rooms.items():
        for cname, cdata in rdata.connections.items():
            if cdata.destination not in STATIC_LOGIC.rooms:
                logging.warning(f"{rname}:{cname} destination room does not exist")
            elif cdata.pair not in STATIC_LOGIC.rooms[cdata.destination].connections:
                logging.warning(f"{rname}:{cname} paired connection does not exist")
            else:
                other_conn = STATIC_LOGIC.rooms[cdata.destination].connections[cdata.pair]

                if other_conn.destination != rname or other_conn.pair != cname or other_conn.type != cdata.type\
                        or other_conn.plane != cdata.plane.opposite():
                    logging.warning(f"{rname}:{cname} does not match paired connection")

    items = set()
    locations = set()
    for room_data in STATIC_LOGIC.rooms.values():
        for conn_data in room_data.connections.values():
            if conn_data.requirements is not None and conn_data.requirements.items is not None:
                for item in conn_data.requirements.items:
                    items.add(item)

        for tree_data in room_data.trees:
            if tree_data.requirements is not None and tree_data.requirements.items is not None:
                for item in tree_data.requirements.items:
                    items.add(item)

        for loc_data in room_data.locations:
            locations.add(loc_data.name)
            if loc_data.requirements is not None and loc_data.requirements.items is not None:
                for item in loc_data.requirements.items:
                    items.add(item)

    items.add("Nothing")

    STATIC_LOGIC.locations = {name: code for code, name in enumerate(locations)}
    STATIC_LOGIC.items = {name: code for code, name in enumerate(items)}

    print(items)
    print(len(items))

    print(locations)
    print(len(locations))


load_static_logic()
