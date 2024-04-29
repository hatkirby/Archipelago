from typing import List

from Options import StartInventoryPool

from . import Constants
from .Options import AnodyneGameOptions, IncludeGreenCubeChest, IncludeWiggleChest, KeyShuffle, StartBroom  # the options we defined earlier
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
    options_dataclass = AnodyneGameOptions
    options: AnodyneGameOptions
    topology_present = False  # show path to required location checks in spoiler

    data_version = 1

    item_name_to_id = Constants.item_name_to_id
    location_name_to_id = Constants.location_name_to_id

    def create_item(self, name: str) -> Item:     
        if name in Constants.item_info["progression_items"]:
            item_class = ItemClassification.progression
        elif name in Constants.item_info["useful_items"]:
            item_class = ItemClassification.useful
        elif name in Constants.item_info["trap_items"]:
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

        #if not green_cube_chest:
            #self.multiworld.exclude_locations[self.player].value.add("Green cube chest")

        #self.create_event("Go", "Defeat Briar")
        #self.create_event("Nexus", "Open 49 card gate")

    def create_items(self) -> None:
        placed_items = 0
        excluded_items:set[str] = {"Jump"} #TODO: Jump is not actually in the item pool atm, in the list to keep ids correct for game

        key_shuffle:KeyShuffle = self.options.key_shuffle
        
        if key_shuffle.current_key == 'vanilla':
            excluded_items.update(
                [
                    "Key",
                    "Key (Apartment)",
                    "Key (Bedroom)",
                    "Key (Circus)",
                    "Key (Crowd)",
                    "Key (Hotel)",
                    "Key (Red Cave)",
                    "Key (Street)"
                    ]
                )
            for location in Constants.location_info["vanilla_key_locations"]:
                placed_items += 1
                self.multiworld.get_location(location, self.player).place_locked_item(self.create_item("Key"))
        
        self.set_starting_broom()

        item_pool: List[AnodyneItem] = []
        for name in Constants.item_info["all_items"]:
            if name not in excluded_items:
                placed_items += 1
                item_pool.append(self.create_item(name))

        if(placed_items < len(Constants.location_name_to_id)):
            item_pool.extend(self.create_filler() for _ in range(len(Constants.location_name_to_id) - placed_items))

        self.multiworld.itempool += item_pool
        

    def get_filler_item_name(self) -> str:
        return "Key"
    
    def set_starting_broom(self):
        start_broom:StartBroom = self.options.start_broom
        start_broom_item:str = ""

        if start_broom.current_key == "normal":
            start_broom_item = "Broom"
        elif start_broom.current_key == "wide":
            start_broom_item = "Wide upgrade"
        elif start_broom.current_key == "long":
            start_broom_item = "Long upgrade"
        elif start_broom.current_key == "swapper":
            start_broom_item = "Swap upgrade"

        if start_broom_item != "":
            self.options.start_inventory_from_pool = StartInventoryPool({start_broom_item: 1})
            #excluded_items.add(start_broom_item)
    
    def fill_slot_data(self):
        return {
            "death_link": self.options.death_link.value
        }