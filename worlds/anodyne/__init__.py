import logging
from typing import Dict, List

from BaseClasses import Tutorial, Item, Location, Region, ItemClassification
from Fill import fill_restrictive, FillError
from worlds.AutoWorld import WebWorld, World
from .data.constants import ANODYNE_DUNGEONS
from .data.items import ANODYNE_ITEMS_BY_NAME, ANODYNE_ITEMS
from .data.locations import LocationData, ANODYNE_LOCATIONS
from .data.logic import AnodyneConnection, get_logic
from .data.regions import ANODYNE_REGIONS
from .functions import build_item_name_to_id_dict, build_location_name_to_id_dict, build_location_by_region_dict
from .options import AnodyneOptions


class AnodyneWebWorld(WebWorld):
    theme = "partyTime"
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to playing Anodyne with Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["hatkirby"]
    )]


class AnodyneItem(Item):
    game = "Anodyne"


class AnodyneLocation(Location):
    game = "Anodyne"


class AnodyneWorld(World):
    """
    Anodyne is a retro adventure game that plays like a combination of Link's Awakening or Yume Nikki. You traverse a
    moody, dreamlike world with the goal of protecting The Legendary Briar from The Darkness, armed only with a broom.
    """
    game = "Anodyne"
    web = AnodyneWebWorld()

    options_dataclass = AnodyneOptions
    options: AnodyneOptions

    item_name_to_id = build_item_name_to_id_dict()
    location_name_to_id = build_location_name_to_id_dict()

    def create_regions(self):
        regions: Dict[str, Region] = {
            "Menu": Region("Menu", self.player, self.multiworld)
        }

        location_by_region: Dict[str, List[LocationData]] = build_location_by_region_dict()

        for region_name in ANODYNE_REGIONS:
            region = Region(region_name, self.player, self.multiworld)

            for location in location_by_region.get(region_name, []):
                new_location = AnodyneLocation(self.player, location.name, self.location_name_to_id[location.name],
                                               region)
                region.locations.append(new_location)

            regions[region_name] = region

        connections: List[AnodyneConnection] = get_logic(self)
        for connection in connections:
            regions[connection.from_region].connect(regions[connection.to_region],
                                                    f"{connection.from_region} to {connection.to_region}",
                                                    connection.rule)

        self.multiworld.regions += regions.values()

        self.create_events()

    def create_events(self):
        self.create_event("briar", "Victory")

    def create_event(self, region_name: str, event_name: str):
        region = self.multiworld.get_region(region_name, self.player)
        location = AnodyneLocation(self.player, f"{event_name} (Reached)", None, region)
        region.locations.append(location)
        location.place_locked_item(AnodyneItem(event_name, ItemClassification.progression, None, self.player))

    def create_items(self):
        pool = []

        real_items = 0
        for item in ANODYNE_ITEMS:
            if item.classification not in [ItemClassification.progression, ItemClassification.useful]:
                continue

            if item.dungeon is not None and not self.options.small_key_shuffle:
                real_items += item.amount
                continue

            for i in range(0, item.amount):
                pool.append(self.create_item(item.name))
                real_items += 1

        item_difference = len(ANODYNE_LOCATIONS) - real_items
        for i in range(0, item_difference):
            pool.append(self.create_item("Heal"))

        self.multiworld.itempool += pool

    def create_item(self, name: str) -> Item:
        item = ANODYNE_ITEMS_BY_NAME[name]

        return AnodyneItem(name, item.classification, self.item_name_to_id[name], self.player)

    def set_rules(self):
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def pre_fill(self):
        collection_state = self.multiworld.get_all_state(False)

        for dungeon in ANODYNE_DUNGEONS:
            dungeon_location_names = [location.name for location in ANODYNE_LOCATIONS if location.dungeon == dungeon]
            dungeon_locations = [location for location in self.multiworld.get_locations(self.player)
                                 if location.name in dungeon_location_names]

            confined_dungeon_items = []
            if not self.options.small_key_shuffle:
                small_key_name = f"Small Key ({dungeon})"
                small_key_item = ANODYNE_ITEMS_BY_NAME[small_key_name]

                for i in range(0, small_key_item.amount):
                    confined_dungeon_items.append(self.create_item(small_key_name))

            if len(confined_dungeon_items) == 0:
                continue

            for item in confined_dungeon_items:
                collection_state.remove(item)

            for attempts_remaining in range(2, -1, -1):
                self.random.shuffle(dungeon_locations)
                try:
                    fill_restrictive(self.multiworld, collection_state, dungeon_locations, confined_dungeon_items,

                                     single_player_placement=True, lock=True, allow_excluded=True)
                    break
                except FillError as exc:
                    if attempts_remaining == 0:
                        raise exc
                    logging.debug(f"Failed to shuffle dungeon items for player {self.player}. Retrying...")

    def get_filler_item_name(self) -> str:
        return "Heal"
