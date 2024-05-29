import logging

from typing import TYPE_CHECKING, List
from BaseClasses import CollectionState
from .Options import KeyShuffle

from .data import Items, Locations

if TYPE_CHECKING:
    from . import AnodyneWorld

id_offset: int = 20130204

item_name_to_id = {name: id for id, name in enumerate(Items.all_items, id_offset)}
location_name_to_id = {location.name: id for id, location in enumerate(Locations.all_locations, id_offset)}


def count_cards(state: CollectionState, world: "AnodyneWorld") -> int:
    card_count = 0
    for card in Items.cards:
        if state.has(card, world.player):
            card_count += 1

    return card_count


def count_keys(state: CollectionState, world: "AnodyneWorld", map_name: str) -> int:
    key_name: str = f"Key ({map_name})"

    if key_name not in Items.all_items:
        return 0
    else:
        return state.count(key_name, world.player)


def check_access(state: CollectionState, world: "AnodyneWorld", rule: str, map_name: str) -> bool:
    if rule == "Combat":
        logging.debug(f"Combat check in {map_name} ({world.player})")
        return state.has_any(items=["Broom", "Wide upgrade", "Long upgrade"], player=world.player)
    elif rule.startswith("Cards:"):
        count = int(rule[6:])
        logging.debug(f"Card {count} check in {map_name} ({world.player})")
        return state.has("Card", world.player, count)
    elif rule.startswith("Keys:"):
        if world.options.key_shuffle == KeyShuffle.option_unlocked:
            logging.debug(f"Gates are unlocked ({world.player})")
            return True

        values = rule.split(":")

        count = int(values[2])
        dungeon_name = values[1]
        logging.debug(f"Key {count} check in {map_name} having {count_keys(state,world,dungeon_name)} ({world.player})")
        return count_keys(state, world, dungeon_name) >= count
    else:
        logging.debug(f"Item {rule} check in {map_name} ({world.player})")
        return state.has(item=rule, player=world.player)


def anodyne_get_access_rule(reqs: List[str], region_name: str, world: "AnodyneWorld"):
    return lambda state: all(check_access(state, world, item, region_name) for item in reqs)
