import os
import json
import pkgutil

id_offset: int = 20130204

def load_data_file(*args) -> dict:
    fname = os.path.join("Data", *args)
    return json.loads(pkgutil.get_data(__name__, fname).decode())

item_info:list[str] = load_data_file("Items.json")
location_info:list[str] = load_data_file("Locations.json")
region_info:list[str] = load_data_file("Locations.json")

item_name_to_id = {name: id for id, name in enumerate(item_info["all_items"], id_offset)}
location_name_to_id = {name: id for id, name in enumerate(location_info["all_locations"], id_offset)}