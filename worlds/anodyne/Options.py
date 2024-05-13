from dataclasses import dataclass
from typing import Dict

from Options import Choice, DeathLink, PerGameCommonOptions, StartInventoryPool, Toggle, Range
from .Data import Regions


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


class NexusGatesOpen(Choice):
    """Select which Nexus Gates are open from the start. Street is always open."""
    display_name = "Nexus Gates opened"
    option_street_only = 0
    option_street_and_fields = 1
    option_early = 2
    option_all = 3
    option_random_count = 4
    default = 1


class RandomNexusGateOpenCount(Range):
    """The amount of random Nexus Gates to be opened from the start. Only has an effect if Nexus Gates is set to
    random."""
    display_name = "Random Nexus Gates open count"
    range_start = 1
    range_end = len(Regions.regions_with_nexus_gate)
    default = 4


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
    nexus_gates_open: NexusGatesOpen
    randomNexusGateOpenCount: RandomNexusGateOpenCount
    victory_condition: VictoryCondition
    green_cube_chest: IncludeGreenCubeChest
    death_link: DeathLink
    start_inventory_from_pool: StartInventoryPool
