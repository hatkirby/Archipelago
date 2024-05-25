from BaseClasses import Region, Location, Item, ItemClassification, CollectionState
from worlds.AutoWorld import WebWorld, World
from typing import List, Callable

from . import Constants

from .Data import Items, Locations, Regions, Exits, Events
from .Options import AnodyneGameOptions, IncludeGreenCubeChest, KeyShuffle, StartBroom, \
    VictoryCondition  # , VictoryCondition


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

    gates_unlocked: list[str] = []

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
        include_health_cicadas = self.options.include_health_cicadas
        include_big_keys = self.options.include_big_keys

        for region_name in Regions.all_regions:
            region = Region(region_name, self.player, self.multiworld)
            if region_name in Locations.locations_by_region:
                for location_name in Locations.locations_by_region[region_name]:
                    if (include_health_cicadas.current_key == "false"
                            and location_name in Locations.health_cicada_locations):
                        continue

                    if include_big_keys.current_key == "false" and location_name in Locations.big_key_locations:
                        continue

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

                        e = r1.create_exit(f"{exit_name} {str(i + 1)}")
                        e.connect(r2)
                        e.access_rule = (lambda reqs, name: (lambda state: (
                            all(Constants.check_access(state, self.player, item, name)
                                for item in reqs))))(requirements, region.name)

            if region.name in Regions.regions_with_nexus_gate:
                gate_name = f"{region.name} Nexus Gate"
                event_name = f"{gate_name} unlocked"

                nexus_region = self.multiworld.get_region("Nexus bottom", self.player)

                self.create_event(region, event_name, lambda state: True)

                e1 = region.create_exit(f"{gate_name} exit 1")
                e1.connect(nexus_region)
                e1.access_rule = ((lambda req, name: (lambda state: (
                    Constants.check_access(state, self.player, req, name))))
                                  (event_name, region.name))

                e2 = nexus_region.create_exit(f"{gate_name} exit 2")
                e2.connect(region)
                e2.access_rule = ((lambda req, name: (lambda state: (
                    Constants.check_access(state, self.player, req, name))))
                                  (event_name, region.name))

            if region.name in Events.events_by_region:
                for event_name in Events.events_by_region[region.name]:
                    if include_big_keys.current_key == "true" and event_name in Events.big_key_events:
                        continue

                    requirements: list[str] = Events.events_by_region[region.name][event_name]
                    self.create_event(region, event_name, (lambda reqs, name: (lambda state: (
                        all(Constants.check_access(state, self.player, item, name)
                            for item in reqs)
                    )))(requirements, region.name))
        from Utils import visualize_regions

        visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")

    def set_rules(self) -> None:
        green_cube_chest = bool(self.options.green_cube_chest)
        nexus_gate_open = self.options.nexus_gates_open

        victory_condition: VictoryCondition = self.options.victory_condition

        requirements: list[str] = []

        if not green_cube_chest:
            self.multiworld.exclude_locations[self.player].value.add("Green cube chest")

        # Street is always unlocked
        if nexus_gate_open == "street_and_fields":
            self.gates_unlocked.append("Fields")
        elif nexus_gate_open == "early":
            for region_name in Regions.early_nexus_gates:
                self.gates_unlocked.append(region_name)
        elif nexus_gate_open == "all":
            for region_name in Regions.regions_with_nexus_gate:
                self.gates_unlocked.append(region_name)
        elif nexus_gate_open == "random_count":
            random_nexus_gate_count = int(self.options.randomNexusGateOpenCount)

            if random_nexus_gate_count == Regions.regions_with_nexus_gate:
                for region_name in Regions.regions_with_nexus_gate:
                    self.gates_unlocked.append(region_name)
            else:
                unused_gates = Regions.regions_with_nexus_gate.copy()
                for _ in range(random_nexus_gate_count):
                    gate_index = self.multiworld.random.randint(0, len(unused_gates) - 1)
                    gate_name = unused_gates[gate_index]

                    self.gates_unlocked.append(gate_name)
                    unused_gates.remove(gate_name)

        for region_name in self.gates_unlocked:
            self.unlock_event(f"{region_name} Nexus Gate unlocked")

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
        item_pool: List[AnodyneItem] = []
        local_item_pool: set[str] = set()
        non_local_item_pool: set[str] = set()

        key_shuffle: KeyShuffle = self.options.key_shuffle

        start_broom: StartBroom = self.options.start_broom
        start_broom_item: str = ""

        include_health_cicadas = self.options.include_health_cicadas
        include_big_keys = self.options.include_big_keys

        placed_items = 0
        location_count = len(Constants.location_name_to_id)

        # TODO: Jump is not actually in the item pool atm, in the list to keep ids correct for game
        excluded_items: set[str] = {
            "Jump shoes",
            "Key",
            "Key (Apartment)",
            "Key (Bedroom)",
            "Key (Circus)",
            "Key (Crowd)",
            "Key (Hotel)",
            "Key (Red Cave)",
            "Key (Street)",
            "Health Cicada"
        }

        if key_shuffle.current_key == "vanilla":
            for region in Locations.vanilla_key_locations:
                for location in Locations.vanilla_key_locations[region]:
                    placed_items += 1
                    self.multiworld.get_location(location, self.player).place_locked_item(
                        self.create_item(f"Key ({region})"))
        elif key_shuffle.current_key != "unlocked":
            for key_item in Items.key_item_count:
                key_count: int = Items.key_item_count[key_item]
                placed_items += key_count

                for _ in range(key_count):
                    item_pool.append(self.create_item(key_item))

                if key_shuffle.current_key == "own_world":
                    local_item_pool.add(key_item)
                elif key_shuffle.current_key == "different_world":
                    non_local_item_pool.add(key_item)

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

        if include_health_cicadas.current_key == "false":
            location_count - len(Locations.health_cicada_locations)
        else:
            for _ in Locations.health_cicada_locations:
                placed_items += 1
                item_pool.append(self.create_item("Health Cicada"))

        if include_big_keys.current_key == "false":
            location_count - len(Locations.big_key_locations)
            excluded_items.update(Items.big_keys)

        for name in Items.all_items:
            if name not in excluded_items:
                placed_items += 1
                item_pool.append(self.create_item(name))

        if placed_items < location_count:
            item_pool.extend(self.create_filler() for _ in range(location_count - placed_items))

        self.multiworld.itempool += item_pool

        self.options.local_items.value |= local_item_pool
        self.options.non_local_items.value |= non_local_item_pool

    def get_filler_item_name(self) -> str:
        return "Key"

    def create_event(self, region: Region, event_name: str, access_rule: Callable[[CollectionState], bool]) -> None:
        loc = AnodyneLocation(self.player, event_name, None, region)
        loc.place_locked_item(self.create_event_item(event_name))
        loc.access_rule = access_rule
        region.locations.append(loc)

    def unlock_event(self, event_name: str):
        self.multiworld.push_precollected(self.get_location(event_name).item)

    def create_event_item(self, name: str) -> Item:
        item = self.create_item(name)
        item.classification = ItemClassification.progression
        return item

    def fill_slot_data(self):
        return {
            "death_link": self.options.death_link.value == 1,
            "unlock_gates": self.options.key_shuffle.value == 1,
            "nexus_gates_unlocked": self.gates_unlocked
        }
