from typing import List

from . import Constants
from .Options import AnodyneGameOptions, IncludeGreenCubeChest, IncludeWiggleChest, KeyShuffle, \
    StartBroom  # the options we defined earlier
from .Rules import get_button_rule
from .Data import Items, Locations

from worlds.AutoWorld import WebWorld, World
from BaseClasses import Region, Entrance, Location, Item, ItemClassification, CollectionState


class AnodyneLocation(Location):
    game = "Anodyne"


class AnodyneItem(Item):
    game = "Anodyne"


class AnodyneWebWorld(WebWorld):
    theme = "dirt"


class AnodyneGameWorld(World):
    """
    Anodyne is a unique Zelda-like game, influenced by games such as Yume Nikki and Link's Awakening. 
    In Anodyne, you'll visit areas urban, natural, and bizarre, fighting your way through dungeons 
    and areas in Young's subconscious.
    """
    game = "Anodyne"  # name of the game/world
    options_dataclass = AnodyneGameOptions
    options: AnodyneGameOptions
    topology_present = False  # show path to required location checks in spoiler

    data_version = 1

    item_name_to_id = Constants.item_name_to_id
    location_name_to_id = Constants.location_name_to_id

    def create_item(self, name: str) -> Item:
        if name in Items.progression_items:
            item_class = ItemClassification.progression
        elif name in Items.useful_items:
            item_class = ItemClassification.useful
        elif name in Items.trap_items:
            item_class = ItemClassification.trap
        else:
            item_class = ItemClassification.filler

        return AnodyneItem(name, item_class, self.item_name_to_id.get(name, None), self.player)

    def create_regions(self) -> None:

        menu = Region("Menu", self.player, self.multiworld)
        world = Region("World", self.player, self.multiworld)

        world.add_locations(Constants.location_name_to_id)

        self.multiworld.regions.append(menu)
        self.multiworld.regions.append(world)

        menu.add_exits(["World"])

        green_cube_chest = bool(self.options.green_cube_chest)

        if not green_cube_chest:
            self.multiworld.exclude_locations[self.player].value.add("Green cube chest")

        #self.create_event("Go", "Defeat Briar")
        #self.create_event("Nexus", "Open 49 card gate")

    def create_items(self) -> None:
        placed_items = 0
        excluded_items: set[str] = {"Jump",
                                    "Key"}
        # TODO: Jump is not actually in the item pool atm, in the list to keep ids correct for game

        key_shuffle: KeyShuffle = self.options.key_shuffle

        if key_shuffle.current_key == "vanilla":
            excluded_items.update(
                [
                    "Key (Apartment)",
                    "Key (Bedroom)",
                    "Key (Circus)",
                    "Key (Crowd)",
                    "Key (Hotel)",
                    "Key (Red Cave)",
                    "Key (Street)"
                ]
            )
            for name in Locations.vanilla_key_locations:
                placed_items += 1
                self.multiworld.get_location(name, self.player).place_locked_item(
                    self.create_item("Key (" + name + ")"))

        start_broom: StartBroom = self.options.start_broom
        start_broom_item: str = ""

        if start_broom.current_key == "normal":
            start_broom_item = "Broom"
        elif start_broom.current_key == "wide":
            start_broom_item = "Wide upgrade"
        elif start_broom.current_key == "long":
            start_broom_item = "Long upgrade"
        elif start_broom.current_key == "swapper":
            start_broom_item = "Swap upgrade"

        if start_broom_item != "":
            self.multiworld.push_precollected(self.create_item(start_broom_item))
            excluded_items.add(start_broom_item)

        item_pool: List[AnodyneItem] = []
        for name in Items.all_items:
            if name not in excluded_items:
                placed_items += 1
                item_pool.append(self.create_item(name))

        if (placed_items < len(Constants.location_name_to_id)):
            item_pool.extend(self.create_filler() for _ in range(len(Constants.location_name_to_id) - placed_items))

        self.multiworld.itempool += item_pool

    def get_filler_item_name(self) -> str:
        return "Key"

    def count_cards(self) -> int:
        card_count = 0
        for card in Items.cards:
            if self.multiworld.state.has(card, self.player):
                card_count += 1

        return card_count

    def count_keys(self, map_name: str) -> int:
        key_name: str = "Key (" + map_name + ")"

        if key_name not in Items.all_items:
            return 0
        else:
            return self.multiworld.state.item_count(key_name, self.player)

    def fill_slot_data(self):
        return {
            "death_link": self.options.death_link.value
        }
