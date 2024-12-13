from enum import Enum
from typing import Optional, List, Dict, Type

import Options
from .utils import DoubleMap, OrderedBijection
from .value import OptionValue, get_random_option_value_from_string
from ..AutoWorld import World

common_option_names = ["start_inventory", "local_items", "non_local_items", "start_hints", "start_location_hints",
                       "exclude_locations", "priority_locations", "start_inventory_from_pool", "item_links"]


def get_html_doc(option_type: type(Options.Option)) -> str:
    if not option_type.__doc__:
        return "Please document me!"
    return "\n".join(line.strip() for line in option_type.__doc__.split("\n")).strip()


class OptionType(Enum):
    UNKNOWN = 0
    RANGE = 1
    SELECT = 2
    SET = 3
    DICT = 4


class SetType(Enum):
    CUSTOM = 1
    ITEM = 2
    LOCATION = 3


class OptionDefinition:
    type: OptionType
    common: bool

    name: str
    display_name: str
    description: str

    min_value: int
    max_value: int
    named_range: bool
    value_names: OrderedBijection[int, str]  # value, display name

    set_type: Optional[SetType]
    custom_set: List[str]

    choices: OrderedBijection[int, str]  # id, name
    choice_names: List[str]
    aliases: Dict[str, str]  # alias, name

    default_value: OptionValue

    def __init__(self, name: str, option: Options.AssembleOptions):
        self.common = (name in common_option_names)
        self.name = name
        self.type = OptionType.UNKNOWN
        self.display_name = option.display_name if hasattr(option, "display_name") else name
        self.description = get_html_doc(option)
        self.default_value = OptionValue()

        if (issubclass(option, Options.Choice) or issubclass(option, Options.Toggle)) and not issubclass(option, Options.TextChoice):
            self.type = OptionType.SELECT
            self.choice_names = []
            self.choices = OrderedBijection()
            self.aliases = {}

            found_default = False
            for sub_option_id, sub_option_name in option.name_lookup.items():
                if sub_option_name != "Random":
                    self.choice_names.append(option.get_option_name(sub_option_id))
                    self.choices.append(sub_option_id, sub_option_name)

                if sub_option_id == option.default:
                    self.default_value.value = sub_option_name
                    found_default = True

            if hasattr(option, "aliases"):
                for alias_name, sub_option_id in option.aliases.items():
                    self.aliases[alias_name] = option.name_lookup[sub_option_id]

            if not found_default:
                self.default_value.random = True

        elif issubclass(option, Options.Range):
            self.type = OptionType.RANGE
            self.min_value = option.range_start
            self.max_value = option.range_end

            if issubclass(option, Options.NamedRange):
                self.named_range = True
                self.value_names = OrderedBijection()

                for key, val in option.special_range_names.items():
                    self.value_names.append(val, key)
            else:
                self.named_range = False

            if hasattr(option, "default"):
                if isinstance(option.default, str):
                    if option.default.startswith("random"):
                        self.default_value = get_random_option_value_from_string(option.default)
                    elif isinstance(self.value_names, OrderedBijection) and option.default in self.value_names.values:
                        self.default_value.value = self.value_names.backward.get(option.default)
                else:
                    self.default_value.value = option.default
            else:
                self.default_value.value = self.min_value

        elif issubclass(option, Options.ItemSet):
            self.type = OptionType.SET
            self.set_type = SetType.ITEM
            self.default_value.value = list(option.default)

        elif issubclass(option, Options.ItemDict):
            self.type = OptionType.DICT
            self.set_type = SetType.ITEM
            self.default_value.value = {value_name: 1 for value_name in list(option.default)}

        elif issubclass(option, Options.LocationSet):
            self.type = OptionType.SET
            self.set_type = SetType.LOCATION
            self.default_value.value = list(option.default)

        #elif issubclass(option, Options.OptionDict):

        elif issubclass(option, Options.OptionList) or issubclass(option, Options.OptionSet):
            if option.valid_keys:
                self.type = OptionType.SET
                self.set_type = SetType.CUSTOM
                self.custom_set = list(option.valid_keys)
                self.default_value.value = list(option.default) if hasattr(option, "default") else []


class Game:
    name: str
    options: Dict[str, OptionDefinition]
    items: List[str]
    locations: List[str]
    presets: Dict[str, Dict[str, OptionValue]]

    def __init__(self, name: str, world: Type[World]):
        self.name = name
        self.options = {}
        self.items = []
        self.locations = []
        self.presets = {}

        for option_name, option in world.options_dataclass.type_hints.items():
            self.options[option_name] = OptionDefinition(option_name, option)

        self.items = list(world.item_names) + list(world.item_name_groups.keys())
        self.items.sort()

        self.locations = list(world.location_names) + list(world.location_name_groups.keys())
        self.locations.sort()

        for preset_name, preset_options in world.web.options_presets.items():
            preset = {}

            for option_name, option_value in preset_options.items():
                game_option = self.options.get(option_name)
                ov = OptionValue()

                if option_value == "random":
                    ov.random = True
                    ov.weighting = None
                elif game_option.type == OptionType.RANGE:
                    if isinstance(option_value, str) and option_value in game_option.value_names.values:
                        ov.value = game_option.value_names.backward.get(option_value)
                    elif isinstance(option_value, int):
                        ov.value = option_value
                elif game_option.type == OptionType.SELECT:
                    if isinstance(option_value, str) and option_value in game_option.choices.values:
                        ov.value = option_value
                    elif isinstance(option_value, int) and option_value in game_option.choices.keys:
                        ov.value = game_option.choices.forward.get(option_value)
                    elif isinstance(option_value, bool):
                        if option_value:
                            ov.value = "true"
                        else:
                            ov.value = "false"
                elif game_option.type == OptionType.SET:
                    option_set = self.get_option_set_elements(game_option)

                    ov.value = [option_set.index(set_item) for set_item in option_value]

                preset[option_name] = ov

            self.presets[preset_name] = preset

    def get_option_set_elements(self, option: OptionDefinition):
        if option.set_type == SetType.ITEM:
            return self.items
        elif option.set_type == SetType.LOCATION:
            return self.locations
        elif option.set_type == SetType.CUSTOM:
            return option.custom_set


class GameDefinitions:
    games: Dict[str, Game]

    def __init__(self):
        self.games = {}

        from worlds.AutoWorld import AutoWorldRegister

        for game_name, world in AutoWorldRegister.world_types.items():
            if game_name == "Archipelago":
                continue

            self.games[game_name] = Game(game_name, world)


GAME_DEFINITIONS: Optional[GameDefinitions] = None


def get_game_definitions() -> GameDefinitions:
    global GAME_DEFINITIONS

    if GAME_DEFINITIONS is None:
        GAME_DEFINITIONS = GameDefinitions()

    return GAME_DEFINITIONS
