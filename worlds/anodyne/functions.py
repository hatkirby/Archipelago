from typing import Dict, List

from .data.constants import ANODYNE_ID_OFFSET
from .data.items import ANODYNE_ITEMS
from .data.locations import ANODYNE_LOCATIONS, LocationData


def build_location_name_to_id_dict() -> Dict[str, int]:
    location_name_to_id: Dict[str, int] = {}
    current_index = ANODYNE_ID_OFFSET
    for location in ANODYNE_LOCATIONS:
        location_name_to_id[location.name] = current_index
        current_index += 1
    return location_name_to_id


def build_item_name_to_id_dict() -> Dict[str, int]:
    item_name_to_id: Dict[str, int] = {}
    current_index = ANODYNE_ID_OFFSET
    for item in ANODYNE_ITEMS:
        item_name_to_id[item.name] = current_index
        current_index += 1
    return item_name_to_id


def build_location_by_region_dict() -> Dict[str, List[LocationData]]:
    location_by_region: Dict[str, List[LocationData]] = {}
    for location in ANODYNE_LOCATIONS:
        location_by_region.setdefault(location.region, []).append(location)
    return location_by_region
