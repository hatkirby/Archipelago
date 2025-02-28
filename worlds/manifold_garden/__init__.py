from BaseClasses import ItemClassification, Tutorial
from worlds.AutoWorld import WebWorld, World
from .datatypes import Requirements, EntranceIdentifier
from .entrances import EntranceRandomizer
from .items import ManifoldGardenItem
from .options import ManifoldGardenOptions
from .regions import create_regions
from .static_logic import STATIC_LOGIC


class ManifoldGardenWebWorld(WebWorld):
    rich_text_options_doc = True
    theme = "party"
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to playing Manifold Garden with Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["hatkirby"]
    )]


class ManifoldGardenWorld(World):
    """
    Manifold Garden is a first person puzzle game in which you explore an Escher-like, non-Euclidean world. Manipulate
    cubes, water, and tetris pieces to solve puzzles and grow a garden of trees.
    """
    game = "Manifold Garden"
    web = ManifoldGardenWebWorld()

    base_id = 20202010
    topology_present = True

    options_dataclass = ManifoldGardenOptions
    options: ManifoldGardenOptions

    item_name_to_id = STATIC_LOGIC.items
    location_name_to_id = STATIC_LOGIC.locations

    er: EntranceRandomizer | None

    def generate_early(self):
        if self.options.room_shuffle.value:
            self.er = EntranceRandomizer(self)
            self.er.randomize()
        else:
            self.er = None

    def create_regions(self):
        create_regions(self)

    def get_entrance_pair(self, entrance: EntranceIdentifier):
        if self.er is not None and entrance in self.er.connection_by_pair:
            return self.er.connection_by_pair[entrance]
        else:
            conn_data = STATIC_LOGIC.rooms[entrance.room].connections[entrance.entrance]
            return EntranceIdentifier(conn_data.destination, conn_data.pair)

    def create_items(self):
        for item_name, item_code in STATIC_LOGIC.items.items():
            item = ManifoldGardenItem(item_name,
                                      ItemClassification.filler if item_name == "Nothing"
                                      else ItemClassification.progression, item_code, self.player)
            self.multiworld.itempool.append(item)

        for i in range(len(STATIC_LOGIC.locations) - len(STATIC_LOGIC.items)):
            item = ManifoldGardenItem("Nothing",
                                      ItemClassification.filler, STATIC_LOGIC.items.get("Nothing"), self.player)
            self.multiworld.itempool.append(item)

    def set_rules(self):
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def fill_slot_data(self):
        slot_data = {}

        if self.er is not None:
            slot_data["connections"] = [[connection.cur_room, connection.exit, connection.other_room,
                                         connection.entrance] for connection in self.er.connections]

        return slot_data
