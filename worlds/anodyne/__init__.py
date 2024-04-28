from typing import List

from . import Constants
from .Options import IncludeGreenCubeChest, IncludeWiggleChest, KeyShuffle, StartBroom, anodyne_options  # the options we defined earlier
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
        elif name in Constants.item_info["filler"]:
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

        wiggle_chest:IncludeWiggleChest = self.options.wiggle_chest

        #if wiggle_chest.current_key == 'false':


        green_cube_chest:IncludeGreenCubeChest = self.options.green_cube_chest

        #if green_cube_chest.current_key == 'false':
            

        start_broom:StartBroom = self.options.start_broom
        start_broom_item:str = ""

        if key_shuffle.current_key == 'normal':
            start_broom_item = "Broom"
        elif key_shuffle.current_key == 'wide':
            start_broom_item = "Wide upgrade"
        elif key_shuffle.current_key == 'long':
            start_broom_item = "Long upgrade"
        elif key_shuffle.current_key == 'swapper':
            start_broom_item = "Swap upgrade"

        if start_broom_item != "":
            excluded_items.add(start_broom_item)

        if green_cube_chest.current_key == 'false':
            name:str = self.random.choice(Constants.item_info["filler"])
            
            excluded_items.add(name)
            
            self.multiworld.get_location("Green cube chest", self.player).place_locked_item(self.create_item(name))

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
    
    def fill_slot_data(self):
        return {
            "death_link": self.options.death_link.value,
            "start_broom": self.options.start_broom.value
        }