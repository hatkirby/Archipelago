import logging
from typing import List, Callable

from . import Constants

from .Data import Items, Locations, Regions, Exits, Events
from .Options import AnodyneGameOptions, IncludeGreenCubeChest, KeyShuffle, StartBroom, \
    VictoryCondition  # , VictoryCondition

from worlds.AutoWorld import WebWorld, World
from BaseClasses import Region, Location, Item, ItemClassification, CollectionState


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
        for region_name in Regions.all_regions:
            region = Region(region_name, self.player, self.multiworld)
            if region_name in Locations.locations_by_region:
                for location_name in Locations.locations_by_region[region_name]:
                    location_id = Constants.location_name_to_id[location_name]
                    requirements: list[str] = Locations.all_locations[location_name]

                    region.add_locations({location_name: location_id})

                    location = self.get_location(location_name)
                    location.access_rule = (lambda reqs, name: (lambda state: (
                        all(Constants.check_access(state, self.player, item, name)
                            for item in reqs)
                    )))(requirements, region.name)

            self.multiworld.regions.append(region)

        for region in self.multiworld.get_regions(self.player):
            if region.name in Exits.exits_by_region:
                for exit_name in Exits.exits_by_region[region.name]:
                    for i, exit_vals in enumerate(Exits.exits_by_region[region.name][exit_name]):
                        exit1: str = exit_vals[0]
                        exit2: str = exit_vals[1]

                        requirements: list[str] = exit_vals[2]

                        r1 = self.multiworld.get_region(exit1, self.player)
                        r2 = self.multiworld.get_region(exit2, self.player)

                        e = r1.create_exit(exit_name + " " + str(i + 1))
                        e.connect(r2)
                        e.access_rule = (lambda reqs, name: (lambda state: (
                            all(Constants.check_access(state, self.player, item, name)
                                for item in reqs))))(requirements, region.name)

            if region.name in Events.events_by_region:
                for event_name in Events.events_by_region[region.name]:
                    requirements: list[str] = Events.events_by_region[region.name][event_name]
                    self.create_event(region, event_name, (lambda reqs, name: (lambda state: (
                        all(Constants.check_access(state, self.player, item, name)
                            for item in requirements)
                    )))(requirements, region.name))

    def set_rules(self) -> None:
        green_cube_chest = bool(self.options.green_cube_chest)

        if not green_cube_chest:
            self.multiworld.exclude_locations[self.player].value.add("Green cube chest")

        victory_condition: VictoryCondition = self.options.victory_condition
        requirements: list[str] = []

        if victory_condition.current_key == "all_bosses":
            requirements.append("Defeat Seer")
            requirements.append("Defeat Rogue")
            requirements.append("Defeat The Wall")
            requirements.append("Defeat Manager")
            requirements.append("Defeat Servants")
            requirements.append("Defeat Watcher")
            requirements.append("Defeat Sage")
            requirements.append("Defeat Briar")
        elif victory_condition.current_key == "all_cards":
            requirements.append("Cards:49")
            requirements.append("Open 49 card gate")

        self.multiworld.completion_condition[self.player] = lambda state: (
            all(Constants.check_access(state, self.player, item, "Event") for item in requirements)
        )

    def create_items(self) -> None:
        placed_items = 0
        excluded_items: set[str] = {"Jump shoes",
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
            for region in Locations.vanilla_key_locations:
                for location in Locations.vanilla_key_locations[region]:
                    placed_items += 1
                    self.multiworld.get_location(location, self.player).place_locked_item(
                        self.create_item(f"Key ({region})"))

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

        if placed_items < len(Constants.location_name_to_id):
            item_pool.extend(self.create_filler() for _ in range(len(Constants.location_name_to_id) - placed_items))

        logging.info("Created items: " + str(len(self.item_names)) +
                     "/" + str(len(Items.all_items)))

        self.multiworld.itempool += item_pool

    def get_filler_item_name(self) -> str:
        return "Key"

    def create_event(self, region: Region, event_name: str, access_rule: Callable[[CollectionState], bool]) -> None:
        loc = AnodyneLocation(self.player, event_name, None, region)
        loc.place_locked_item(self.create_event_item(event_name))
        loc.access_rule = access_rule
        region.locations.append(loc)

    def create_event_item(self, name: str) -> Item:
        item = self.create_item(name)
        item.classification = ItemClassification.progression
        return item

    def fill_slot_data(self):
        return {
            "death_link": self.options.death_link.value
        }
