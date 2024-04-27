from typing import Dict

from Options import Choice, Option, Toggle

class StartBroom(Choice):
    """Select which broom to start with"""
    display_name = "Starting Broom"
    option_normal = 0
    option_wide = 1
    option_long = 2
    option_swapper = 3
    option_none = 4



class DeathLink(Toggle):
    """When you die, everyone dies! The reverse is true too."""
    display_name = "Death Link"



anodyne_options: Dict[str, type(Option)] = {
    "start_broom": StartBroom,
    "death_link": DeathLink,
}
