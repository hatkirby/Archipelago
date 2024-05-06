from typing import Callable, Dict, NamedTuple
from BaseClasses import MultiWorld, CollectionState

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


def count_cards(state: CollectionState, player: int) -> int:
    card_count = 0
    for card in Items.cards:
        if state.has(card, player):
            card_count += 1

    return card_count


def count_keys(state: CollectionState, player: int, map_name: str) -> int:
    key_name: str = "Key (" + map_name + ")"

    if key_name not in Items.all_items:
        return 0
    else:
        return state.count(key_name, player)


def check_access(state: CollectionState, player: int, rule: str, map_name: str) -> bool:
    if rule == "Any Broom but swapper":
        return state.has_any(items=["Broom", "Wide upgrade", "Long upgrade"], player=player)
    elif rule.startswith("Cards:"):
        count = int(rule[6:])
        return count >= count_cards(state, player)
    elif rule.startswith("Keys:"):
        count = int(rule[5:])
        return count >= count_keys(state, player, map_name)
    else:
        return state.has(item=rule, player=player)
