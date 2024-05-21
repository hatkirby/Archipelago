from typing import Dict, List, Optional, NamedTuple

from BaseClasses import ItemClassification
from .constants import ANODYNE_DUNGEONS


class ItemData(NamedTuple):
    name: str
    classification: ItemClassification = ItemClassification.progression
    dungeon: Optional[str] = None
    amount: int = 1


def create_dungeon_small_key(dungeon: str, amount: int):
    return ItemData(f"Small Key ({dungeon})", dungeon=dungeon, amount=amount)


ANODYNE_ITEMS: List[ItemData] = [
    ItemData("Card", amount=37),

    ItemData("Swap"),

    create_dungeon_small_key("Temple of the Seeing One", 3),
    create_dungeon_small_key("Apartment", 4),
    create_dungeon_small_key("Mountain Cavern", 4),
    create_dungeon_small_key("Hotel", 6),
    create_dungeon_small_key("Red Grotto", 6),
    create_dungeon_small_key("Circus", 4),

    ItemData("Progressive Red Grotto", amount=3),

    ItemData("Green Key"),
    ItemData("Blue Key"),
    ItemData("Red Key"),

    ItemData("Cardboard Box"),
    ItemData("Biking Shoes"),
    ItemData("Jump Shoes"),

    ItemData("Temple of the Seeing One Statue"),
    ItemData("Mountain Cavern Statue"),
    ItemData("Red Grotto Statue"),

    ItemData("Health Cicada", classification=ItemClassification.useful, amount=10),
    ItemData("Extend", classification=ItemClassification.useful),
    ItemData("Widen", classification=ItemClassification.useful),

    ItemData("Heal", classification=ItemClassification.filler),
]

ANODYNE_ITEMS_BY_NAME: Dict[str, ItemData] = {item.name: item for item in ANODYNE_ITEMS}
