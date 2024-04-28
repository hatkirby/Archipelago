from typing import Dict

from Options import Choice, Option, Toggle

class KeyShuffle(Choice):
    """Select which broom to start with"""
    display_name = "Shuffle small keys"
    option_vanilla = 0
    option_original_dungeon = 1
    option_own_dungeons = 2
    option_own_world = 3
    option_any_world = 4
    option_different_world = 5

class StartBroom(Choice):
    """Select which broom to start with."""
    display_name = "Starting Broom"
    option_normal = 0
    option_wide = 1
    option_long = 2
    option_swapper = 3
    option_none = 4

class IncludeWiggleChest(Toggle):
    """Include the chest that requires the wiggle glitch to get to."""
    display_name = "Include wiggle chest"

class IncludeGreenCubeChest(Toggle):
    """Include the chest that forces you to wait almost 2 hours to access it."""
    display_name = "Include green cube chest"

class DeathLink(Toggle):
    """When you die, everyone dies! The reverse is true too."""
    display_name = "Death Link"

anodyne_options: Dict[str, type(Option)] = {
    "key_shuffle" : KeyShuffle,
    "start_broom": StartBroom,
    "wiggle_chest" : IncludeWiggleChest,
    "green_cube_chest" : IncludeGreenCubeChest,
    "death_link": DeathLink,
}
