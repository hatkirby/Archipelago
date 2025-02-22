import os
import sys
import yaml


NEXT_ITEM_ID = 20202010
NEXT_LOCATION_ID = 20202010


def allocate_item_id():
    global NEXT_ITEM_ID
    next_id = NEXT_ITEM_ID
    NEXT_ITEM_ID += 1
    return next_id


def allocate_location_id():
    global NEXT_LOCATION_ID
    next_id = NEXT_LOCATION_ID
    NEXT_LOCATION_ID += 1
    return next_id


def assign_ids(config_path, output_path):
    global NEXT_ITEM_ID, NEXT_LOCATION_ID

    with open(config_path, "r") as file:
        config = yaml.load(file, Loader=yaml.Loader)

    if os.path.exists(output_path):
        with open(output_path, "r") as file:
            ids = yaml.load(file, Loader=yaml.Loader)

        NEXT_LOCATION_ID = max(ids["locations"].values()) + 1
        NEXT_ITEM_ID = max(ids["items"].values()) + 1
    else:
        ids = {"locations": {}, "items": {}}

    all_locations = set()
    all_items = set()

    for scene_data in config.values():
        if "locations" in scene_data:
            for location_data in scene_data["locations"]:
                if isinstance(location_data, dict):
                    all_locations.add(location_data["name"])
                    if "item" in location_data:
                        if isinstance(location_data["item"], list):
                            for item_name in location_data["item"]:
                                all_items.add(item_name)
                        else:
                            all_items.add(location_data["item"])
                else:
                    all_locations.add(location_data)

        if "connections" in scene_data:
            for connection_data in scene_data["connections"].values():
                if "item" in connection_data:
                    if isinstance(connection_data["item"], list):
                        for item_name in connection_data["item"]:
                            all_items.add(item_name)
                    else:
                        all_items.add(connection_data["item"])

        if "cubes" in scene_data:
            for cube_data in scene_data["cubes"]:
                if "item" in cube_data:
                    if isinstance(cube_data["item"], list):
                        for item_name in cube_data["item"]:
                            all_items.add(item_name)
                    else:
                        all_items.add(cube_data["item"])

    for location in all_locations:
        if location not in ids["locations"]:
            ids["locations"][location] = allocate_location_id()

    for item in all_items:
        if item not in ids["items"]:
            ids["items"][item] = allocate_item_id()

    with open(output_path, "w") as file:
        yaml.dump(ids, file)

    print(f"Next location ID: {NEXT_LOCATION_ID}")
    print(f"Next item ID: {NEXT_ITEM_ID}")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        config_path = os.path.join("worlds", "manifold_garden", "data", "world.yaml")
        output_path = os.path.join("worlds", "manifold_garden", "data", "ids.yaml")
    elif len(sys.argv) != 3:
        print("")
        print("Usage: python worlds/manifold_garden/utils/assign_ids.py [args]")
        print("Arguments:")
        print(" - Path to world.yaml")
        print(" - Path to output file")

        exit()
    else:
        config_path = sys.argv[1]
        output_path = sys.argv[2]

    assign_ids(config_path, output_path)
