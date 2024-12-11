from typing import Optional, Callable, Dict

from .definitions import OptionValue


class Slot:
    name: str
    filename: Optional[str]
    description: str

    options: Dict[str, OptionValue]

    meta_update_callback: Callable[[], None]

    def __init__(self):
        self._dirty = False

        self.name = ""
        self._game = None
        self.filename = None
        self.description = ""

        self.options = {}

        self.meta_update_callback = lambda: None

    def load(self, path: str):
        pass

    def save(self, path: str):
        pass

    def from_yaml(self, text: str):
        pass

    def to_yaml(self) -> str:
        pass

    def set_option(self, option_name: str, option_value: OptionValue):
        pass

    def has_set_options(self) -> bool:
        pass

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        self._dirty = value

        self.meta_update_callback()

    @property
    def game(self) -> Optional[str]:
        return self._game

    @game.setter
    def game(self, value):
        self._game = value
