from typing import List

from . import Constants
from .Options import anodyne_options  # the options we defined earlier
from .Rules import get_button_rule

from worlds.AutoWorld import WebWorld, World
from BaseClasses import Region, Entrance, Location, Item, ItemClassification


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
    option_definitions = anodyne_options
    topology_present = True  # show path to required location checks in spoiler

    item_name_to_id = Constants.item_name_to_id
    location_name_to_id = Constants.location_name_to_id


    def create_item(self, name: str) -> Item:
        item_class = ItemClassification.filler
        if name in Constants.item_info["progression_items"]:
            item_class = ItemClassification.progression
        elif name in Constants.item_info["useful_items"]:
            item_class = ItemClassification.useful
        elif name in Constants.item_info["trap_items"]:
            item_class = ItemClassification.trap

        return AnodyneItem(name, item_class, self.item_name_to_id.get(name, None), self.player)

    def create_event(self, region_name: str, event_name: str) -> None:
        region = self.multiworld.get_region(region_name, self.player)
        loc = AnodyneLocation(self.player, event_name, None, region)
        loc.place_locked_item(self.create_event_item(event_name))
        region.locations.append(loc)

    def create_event_item(self, name: str) -> None:
        item = self.create_item(name)
        item.classification = ItemClassification.progression
        return item

    def create_regions(self) -> None:
        
        menu = Region("Menu", self.player, self.multiworld)
        world = Region("World", self.player, self.multiworld)

        menu.add_exits(self.player, "Start Game", world)
        self.multiworld.regions.append(menu)
    
        #self.create_event("Go", "Defeat Briar")
        #self.create_event("Nexus", "Open 49 card gate")

    def create_items(self) -> None:
        item_pool: List[AnodyneItem] = []
        for name in Constants.item_info["all_items"]:
            item_pool.append(self.create_item(name))

        self.multiworld.itempool += item_pool