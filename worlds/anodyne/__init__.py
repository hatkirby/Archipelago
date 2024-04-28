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
        if name in Constants.item_info["progression_items"]:
            item_class = ItemClassification.progression
        elif name in Constants.item_info["useful_items"]:
            item_class = ItemClassification.useful
        elif name in Constants.item_info["trap_items"]:
            item_class = ItemClassification.trap
        else :
            item_class = ItemClassification.filler

        return AnodyneItem(name, item_class, self.item_name_to_id.get(name, None), self.player)

    def create_regions(self) -> None:
        
        menu = Region("Menu", self.player, self.multiworld)
        world = Region("World", self.player, self.multiworld)

        world.add_locations(Constants.location_name_to_id)

        self.multiworld.regions.append(menu)
        self.multiworld.regions.append(world)
    
        menu.add_exits(["World"])

        #self.create_event("Go", "Defeat Briar")
        #self.create_event("Nexus", "Open 49 card gate")

    def create_items(self) -> None:
        item_pool: List[AnodyneItem] = []
        for name in Constants.item_info["all_items"]:
            item_pool.append(self.create_item(name))

        if(len(item_pool) < len(Constants.location_name_to_id)):
            item_pool.extend(self.create_filler() for _ in range(len(Constants.location_name_to_id) - len(item_pool)))

        self.multiworld.itempool += item_pool
        

    def get_filler_item_name(self) -> str:
        return "Key"