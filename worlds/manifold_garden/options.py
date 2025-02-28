from dataclasses import dataclass

from Options import Choice, Toggle, PerGameCommonOptions, StartInventoryPool


class RoomShuffle(Toggle):
    """When enabled, randomizes the entrances between rooms."""
    display_name = "Room Shuffle"


class RainbowEntranceCondition(Choice):
    """This option specifies how the door to the final area opens.

    - **All God Cubes**: The six single-colored god cubes must all be planted in the garden in order to open the final
      door.
    - **Items**: The six items that grow the gardens are needed to open the final door.
    """
    display_name = "Rainbow Entrance Condition"
    option_all_god_cubes = 0
    option_items = 1


class ApartmentsWaterwheelPuzzle(Toggle):
    """
    The Apartments Waterwheel puzzle is notably tedious and requires carrying nine blue cubes from various rooms into
    the Blue Pyramid / Apartments area. If disabled, solving this puzzle will do nothing. If enabled, solving it will be
    a location check. Additionally, if Room Shuffle is on and this puzzle is enabled, the connection between Blue
    Pyramid and Apartments will be forced vanilla, in order to ensure that it remains possible."""
    display_name = "Apartments Waterwheel Puzzle"


@dataclass
class ManifoldGardenOptions(PerGameCommonOptions):
    room_shuffle: RoomShuffle
    rainbow_entrance_condition: RainbowEntranceCondition
    apartments_waterwheel_puzzle: ApartmentsWaterwheelPuzzle
    start_inventory_from_pool: StartInventoryPool
