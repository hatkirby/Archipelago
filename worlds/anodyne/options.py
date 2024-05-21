from dataclasses import dataclass

from Options import PerGameCommonOptions, Range, StartInventoryPool


class EndgameCardRequirement(Range):
    """The number of cards needed to open the gate that leads to the endgame area.
    Setting this to zero removes the gate."""
    display_name = "Terminal Card Requirement"
    range_start = 0
    range_end = 37
    default = 36


@dataclass
class AnodyneOptions(PerGameCommonOptions):
    endgame_card_requirement: EndgameCardRequirement
    start_inventory_from_pool: StartInventoryPool
