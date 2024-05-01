from typing import Callable, Dict, NamedTuple
from BaseClasses import MultiWorld

from .Data import Items, Locations

id_offset: int = 20130204


class AnodyneExitConnection(NamedTuple):
    region1: str
    region2: str
    access_rule: Callable[[MultiWorld, int], bool] = lambda multiworld, player: True


class AnodyneExitInfo(NamedTuple):
    connections: list[AnodyneExitConnection]
    access_rule: Callable[[MultiWorld, int], bool] = lambda multiworld, player: True


item_name_to_id = {name: id for id, name in enumerate(Items.all_items, id_offset)}
location_name_to_id = {name: id for id, name in enumerate(Locations.all_locations, id_offset)}
