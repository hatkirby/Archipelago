from dataclasses import dataclass
from typing import Dict

from Options import Choice, DeathLink, PerGameCommonOptions, StartInventoryPool, Toggle


class KeyShuffle(Choice):
    """Select which broom to start with"""
    display_name = "Shuffle small keys"
    option_vanilla = 0
    option_unlocked = 1
    option_original_dungeon = 2
    option_own_dungeons = 3
    option_own_world = 4
    option_any_world = 5
    option_different_world = 6
    default = 0

class StartBroom(Choice):
    """Select which broom to start with."""
    display_name = "Starting Broom"
    option_none = 0
    option_normal = 1
    option_wide = 2
    option_long = 3
    option_swap = 4
    default = 0

class VictoryCondition(Choice):
    """Select the end goal of your game."""
    display_name = "Victory condition"
    option_all_bosses = 0
    option_all_cards = 1
    default = 0

class IncludeGreenCubeChest(Toggle):
    """Include the chest that forces you to wait almost 2 hours to access it."""
    display_name = "Include green cube chest"

@dataclass
class AnodyneGameOptions(PerGameCommonOptions):
    key_shuffle: KeyShuffle
    start_broom: StartBroom
    victory_condition: VictoryCondition
    green_cube_chest: IncludeGreenCubeChest
    death_link: DeathLink
    start_inventory_from_pool: StartInventoryPool