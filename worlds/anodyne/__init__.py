from typing import Dict, List

from BaseClasses import Tutorial, Item, Location, Region, ItemClassification
from worlds.AutoWorld import WebWorld, World
from .data.items import ANODYNE_ITEMS_BY_NAME, ANODYNE_ITEMS
from .data.locations import LocationData, ANODYNE_LOCATIONS
from .data.logic import AnodyneConnection, get_logic
from .data.regions import ANODYNE_REGIONS
from .functions import build_item_name_to_id_dict, build_location_name_to_id_dict, build_location_by_region_dict
from .options import AnodyneOptions


class AnodyneWebWorld(WebWorld):
    theme = "desert"
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
    Anodyne is
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

        for item in ANODYNE_ITEMS:
            if item.classification not in [ItemClassification.progression, ItemClassification.useful]:
                continue

            for i in range(0, item.amount):
                pool.append(self.create_item(item.name))

        item_difference = len(ANODYNE_LOCATIONS) - len(pool)
        for i in range(0, item_difference):
            pool.append(self.create_item("Heal"))

        self.multiworld.itempool += pool

    def create_item(self, name: str) -> Item:
        item = ANODYNE_ITEMS_BY_NAME[name]

        return AnodyneItem(name, item.classification, self.item_name_to_id[name], self.player)

    def set_rules(self):
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def get_filler_item_name(self) -> str:
        return "Heal"
