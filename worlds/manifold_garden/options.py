from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, StartInventoryPool


class RainbowEntranceCondition(Choice):
    """This option specifies how the door to the final area opens.

    - **All God Cubes**: The six single-colored god cubes must all be planted in the garden in order to open the final
      door.
    - **Items**: The six items that grow the gardens are needed to open the final door.
    """
    display_name = "Rainbow Entrance Condition"
    option_all_god_cubes = 0
    option_items = 1


@dataclass
class ManifoldGardenOptions(PerGameCommonOptions):
    rainbow_entrance_condition: RainbowEntranceCondition
    start_inventory_from_pool: StartInventoryPool
