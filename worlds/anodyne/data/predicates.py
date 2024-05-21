from typing import TYPE_CHECKING

from BaseClasses import CollectionState

if TYPE_CHECKING:
    from worlds.anodyne import AnodyneWorld


def anodyne_has_cards(state: CollectionState, amount: int, world: "AnodyneWorld"):
    return state.has("Card", world.player, amount)


def anodyne_has_small_keys(state: CollectionState, level: str, minimum: int, world: "AnodyneWorld"):
    return state.has(f"Small Key ({level})", world.player, minimum)


def anodyne_has_red_grotto(state, amount: int, world: "AnodyneWorld"):
    return state.has("Progressive Red Grotto", world.player, amount)
