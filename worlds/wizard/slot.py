from typing import Optional, Callable, Dict, Any

import yaml

import Utils
from .definitions import OptionValue, get_game_definitions, OptionType, OptionDefinition
from .value import random_option_value_to_string, get_random_option_value_from_string


def get_option_value_for_choice_value(option: OptionDefinition, yaml_value: Any) -> OptionValue:
    option_value = OptionValue()

    str_val = str(yaml_value)
    if isinstance(yaml_value, bool):
        option_value.value = str_val.lower()
    elif str_val in option.choices.values:
        option_value.value = str_val
    elif str_val in option.aliases:
        option_value.value = option.aliases.get(str_val)
    elif str_val == "random":
        option_value.random = True
        option_value.weighting = None
    else:
        try:
            int_val = int(str_val)

            if int_val in option.choices.keys:
                option_value.value = option.choices.forward.get(int_val)
            else:
                option_value.error = f"Unknown choice ID \"{int_val}\"."
        except ValueError:
            option_value.error = f"Unknown value \"{str_val}\"."

    return option_value


def get_option_value_for_range_value(option: OptionDefinition, yaml_value: Any) -> OptionValue:
    option_value = OptionValue()

    str_val = str(yaml_value)
    if str_val.startswith("random"):
        option_value = get_random_option_value_from_string(str_val)
    elif option.named_range and str_val in option.value_names.values:
        option_value.value = option.value_names.backward.get(str_val)
    else:
        try:
            option_value.value = int(str_val)

            # Named values allow us to go outside the range
            if not option.named_range or option_value.value not in option.value_names.keys:
                if option_value.value < option.min_value:
                    option_value.error = f"Value {option_value.value} is too small."
                elif option_value.value > option.max_value:
                    option_value.error = f"Value {option_value.value} is too large."
        except ValueError:
            option_value.error = f"Invalid value \"{str_val}\"."

    return option_value


class Slot:
    filename: Optional[str]
    options: Dict[str, OptionValue]
    yaml: Dict[str, Any]
    meta_update_callback: Callable[[], None]

    def __init__(self):
        self._dirty = False

        self._name = ""
        self._game = None
        self._description = ""
        self.filename = None

        self.options = {}
        self.yaml = {}

        self.meta_update_callback = lambda: None

    def load(self, path: str):
        with open(path, "r") as file:
            self.yaml = Utils.parse_yaml(file)

        self.filename = path
        self.populate_from_yaml()

    def save(self, path: str):
        with open(path, "w") as file:
            file.write(self.to_yaml())

        self.dirty = False

    def from_yaml(self, text: str):
        old_node = self.yaml
        self.yaml = Utils.parse_yaml(text)

        try:
            self.populate_from_yaml()
        except Exception as ex:
            self.yaml = old_node
            raise

    def to_yaml(self) -> str:
        return yaml.dump(self.yaml, sort_keys=False)

    def set_option(self, option_name: str, option_value: Optional[OptionValue]):
        if not self.dirty:
            self.dirty = True

        if option_name in self.yaml[self._game]:
            del self.yaml[self._game][option_name]

        if option_value is None:
            del self.options[option_name]

            if len(self.yaml[self.game]) == 0:
                del self.yaml[self.game]

            return

        game = get_game_definitions().games.get(self.game)
        game_option = game.options.get(option_name)

        if game_option.type == OptionType.SELECT:
            if option_value.random:
                if option_value.weighting is None:
                    self.yaml[self.game][option_name] = "random"
                else:
                    self.yaml[self.game][option_name] = {}

                    for weight_value in option_value.weighting:
                        value_text = weight_value.value
                        if weight_value.value == "true":
                            value_text = True
                        elif weight_value.value == "false":
                            value_text = False
                        self.yaml[self.game][option_name][value_text] = weight_value.weight
            else:
                value_text = option_value.value
                if option_value.value == "true":
                    value_text = True
                elif option_value.value == "false":
                    value_text = False
                self.yaml[self.game][option_name] = value_text
        elif game_option.type == OptionType.RANGE:
            if option_value.random:
                if option_value.weighting is None:
                    self.yaml[self.game][option_name] = random_option_value_to_string(option_value)
                else:
                    self.yaml[self.game][option_name] = {}

                    for weight_value in option_value.weighting:
                        string_value = weight_value.value
                        if weight_value.random:
                            string_value = random_option_value_to_string(weight_value)
                        elif game_option.named_range and weight_value.value in game_option.value_names:
                            string_value = game_option.value_names.forward.get(weight_value.value)

                        self.yaml[self.game][option_name][string_value] = weight_value.weight
            elif game_option.named_range and option_value.value in game_option.value_names.keys:
                self.yaml[self.game][option_name] = game_option.value_names.forward.get(option_value.value)
            else:
                self.yaml[self.game][option_name] = option_value.value
        elif game_option.type == OptionType.SET:
            option_set = game.get_option_set_elements(game_option)

            self.yaml[self.game][option_name] = [option_set[i] for i in option_value.value]
        elif game_option.type == OptionType.DICT:
            option_set = game.get_option_set_elements(game_option)

            self.yaml[self.game][option_name] = {option_set[key]: value for key, value in option_value.value.items()}

        self.options[option_name] = option_value

    def clear_options(self):
        self.options.clear()
        self.dirty = True

    def has_set_options(self) -> bool:
        return len(self.options) > 0

    def populate_from_yaml(self):
        if "game" in self.yaml and self.yaml["game"] not in get_game_definitions().games:
            raise Exception(f"Game \"{self.yaml['game']}\" is not supported.")

        self.options.clear()

        if "name" in self.yaml:
            self._name = self.yaml["name"]

        if "description" in self.yaml:
            self._description = self.yaml["description"]

        if "game" in self.yaml:
            self._game = self.yaml["game"]

            if self.yaml[self.game]:
                game_node = self.yaml[self.game]
                game = get_game_definitions().games.get(self.game)

                for option in game.options.values():
                    if option.name in game_node:
                        option_value = OptionValue()

                        if option.type in [OptionType.SELECT, OptionType.RANGE]:
                            # Choices and ranges can be weighted.
                            if isinstance(game_node[option.name], int) or isinstance(game_node[option.name], str):
                                if option.type == OptionType.SELECT:
                                    option_value = get_option_value_for_choice_value(option, game_node[option.name])
                                elif option.type == OptionType.RANGE:
                                    option_value = get_option_value_for_range_value(option, game_node[option.name])
                            elif isinstance(game_node[option.name], dict):
                                option_value.random = True
                                option_value.weighting = []

                                errors = []

                                for weight_value, weighting in game_node[option.name].items():
                                    sub_option_value: OptionValue

                                    if option.type == OptionType.SELECT:
                                        sub_option_value = get_option_value_for_choice_value(option, weight_value)
                                    elif option.type == OptionType.RANGE:
                                        sub_option_value = get_option_value_for_range_value(option, weight_value)
                                    else:
                                        # Can't happen, but let's appease the typechecker.
                                        sub_option_value = OptionValue()

                                    if sub_option_value.error is not None:
                                        errors.append(sub_option_value.error)

                                    try:
                                        sub_option_value.weight = int(weighting)

                                        if sub_option_value.weight > 0:
                                            option_value.weighting.append(sub_option_value)
                                    except ValueError:
                                        errors.append(f"Weight value \"{weighting}\" is not numeric.")

                                if len(option_value.weighting) == 1:
                                    option_value = option_value.weighting[0]

                                if len(errors) > 0:
                                    option_value.error = " ".join(errors)
                        elif option.type == OptionType.SET:
                            if isinstance(game_node[option.name], list):
                                option_set = game.get_option_set_elements(option)

                                option_value.value = []
                                errors = []

                                for set_value in game_node[option.name]:
                                    if set_value in option_set:
                                        option_value.value.append(option_set.index(set_value))
                                    else:
                                        errors.append(f"Invalid value \"{set_value}\".")

                                if len(errors) > 0:
                                    option_value.error = " ".join(errors)
                            else:
                                option_value.error = "Option value should be a list."
                        elif option.type == OptionType.DICT:
                            # Handle dicts
                            if isinstance(game_node[option.name], dict):
                                option_set = game.get_option_set_elements(option)

                                option_value.value = {}
                                errors = []

                                for set_value, int_value in game_node[option.name].items():
                                    # TODO: Non-int values?
                                    if set_value in option_set:
                                        option_value.value[set_value] = int_value
                                    else:
                                        errors.append(f"Invalid value \"{set_value}\".")

                                if len(errors) > 0:
                                    option_value.error = " ".join(errors)
                            else:
                                option_value.error = "Option value should be a map."

                        self.options[option.name] = option_value

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        self._dirty = value

        self.meta_update_callback()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

        self.yaml["name"] = value

        self.meta_update_callback()

    @property
    def game(self) -> Optional[str]:
        return self._game

    @game.setter
    def game(self, value):
        if self._game is not None:
            if self._game in self.yaml:
                del self.yaml[self._game]

            self.options.clear()

        if value is not None:
            self.yaml["game"] = value
            self.yaml[value] = {}
        else:
            del self.yaml["game"]

        self._game = value
        self.dirty = True

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

        self.yaml["description"] = value
