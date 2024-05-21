from dataclasses import dataclass

from Options import PerGameCommonOptions, Range, StartInventoryPool, Toggle


class EndgameCardRequirement(Range):
    """
    The number of cards needed to open the gate that leads to the endgame area.
    Setting this to zero removes the gate.
    """
    display_name = "Terminal Card Requirement"
    range_start = 0
    range_end = 37
    default = 36


class SmallKeyShuffle(Toggle):
    """
    If enabled, small keys will be shuffled everywhere, instead of being confined to their own dungeons.
    """
    display_name = "Small Key Shuffle"


@dataclass
class AnodyneOptions(PerGameCommonOptions):
    endgame_card_requirement: EndgameCardRequirement
    small_key_shuffle: SmallKeyShuffle
    start_inventory_from_pool: StartInventoryPool
