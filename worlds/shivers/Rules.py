from typing import Dict, List, TYPE_CHECKING
from collections.abc import Callable
from BaseClasses import CollectionState
from worlds.generic.Rules import forbid_item

if TYPE_CHECKING:
    from . import ShiversWorld


def water_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (state.can_reach("Lobby", "Region", world.player)
            or (state.can_reach("Janitor Closet", "Region", world.player) and cloth_capturable(state, world))) \
        and state.has_all({"Water Pot Bottom", "Water Pot Top", "Water Pot Bottom DUPE", "Water Pot Top DUPE"},
                          world.player)


def wax_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (state.can_reach("Library", "Region", world.player) or state.can_reach("Anansi", "Region", world.player)) \
        and state.has_all({"Wax Pot Bottom", "Wax Pot Top", "Wax Pot Bottom DUPE", "Wax Pot Top DUPE"}, world.player)


def ash_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (state.can_reach("Office", "Region", world.player) or state.can_reach("Burial", "Region", world.player)) \
        and state.has_all({"Ash Pot Bottom", "Ash Pot Top", "Ash Pot Bottom DUPE", "Ash Pot Top DUPE"}, world.player)


def oil_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (state.can_reach("Prehistoric", "Region", world.player)
            or state.can_reach("Tar River", "Region", world.player)) \
        and state.has_all({"Oil Pot Bottom", "Oil Pot Top", "Oil Pot Bottom DUPE", "Oil Pot Top DUPE"}, world.player)


def cloth_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (state.can_reach("Egypt", "Region", world.player) or state.can_reach("Burial", "Region", world.player)
            or state.can_reach("Janitor Closet", "Region", world.player)) \
        and state.has_all({"Cloth Pot Bottom", "Cloth Pot Top", "Cloth Pot Bottom DUPE", "Cloth Pot Top DUPE"},
                          world.player)


def wood_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (state.can_reach("Workshop", "Region", world.player) or state.can_reach("Blue Maze", "Region", world.player)
            or state.can_reach("Gods Room", "Region", world.player)
            or state.can_reach("Anansi", "Region", world.player)) \
        and state.has_all({"Wood Pot Bottom", "Wood Pot Top", "Wood Pot Bottom DUPE", "Wood Pot Top DUPE"},
                          world.player)


def crystal_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (state.can_reach("Lobby", "Region", world.player) or state.can_reach("Ocean", "Region", world.player)) \
        and state.has_all({"Crystal Pot Bottom", "Crystal Pot Top", "Crystal Pot Bottom DUPE", "Crystal Pot Top DUPE"},
                          world.player)


def sand_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (state.can_reach("Greenhouse", "Region", world.player) or state.can_reach("Ocean", "Region", world.player)) \
        and state.has_all({"Sand Pot Bottom", "Sand Pot Top", "Sand Pot Bottom DUPE", "Sand Pot Top DUPE"},
                          world.player)


def metal_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (state.can_reach("Projector Room", "Region", world.player)
            or state.can_reach("Prehistoric", "Region", world.player)
            or state.can_reach("Bedroom", "Region", world.player)) \
        and state.has_all({"Metal Pot Bottom", "Metal Pot Top", "Metal Pot Bottom DUPE", "Metal Pot Top DUPE"},
                          world.player)


def lightning_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return (first_nine_ixupi_capturable(state, world) or world.options.early_lightning) \
        and state.can_reach("Generator", "Region", world.player) \
        and state.has_all({"Lightning Pot Bottom", "Lightning Pot Top", "Lightning Pot Bottom DUPE",
                           "Lightning Pot Top DUPE"}, world.player)


def beths_body_available(state: CollectionState, world: "ShiversWorld") -> bool:
    return (first_nine_ixupi_capturable(state, world) or world.options.early_beth) \
        and state.can_reach("Generator", "Region", world.player)


def first_nine_ixupi_capturable(state: CollectionState, world: "ShiversWorld") -> bool:
    return water_capturable(state, world) and wax_capturable(state, world) \
        and ash_capturable(state, world) and oil_capturable(state, world) \
        and cloth_capturable(state, world) and wood_capturable(state, world) \
        and crystal_capturable(state, world) and sand_capturable(state, world) \
        and metal_capturable(state, world)


def all_skull_dials_available(state: CollectionState, world: "ShiversWorld") -> bool:
    return state.can_reach("Prehistoric", "Region", world.player)\
        and state.can_reach("Tar River", "Region", world.player) \
        and state.can_reach("Egypt", "Region", world.player) and state.can_reach("Burial", "Region", world.player) \
        and state.can_reach("Gods Room", "Region", world.player) and state.can_reach("Werewolf", "Region", world.player)


def get_rules_lookup(world: "ShiversWorld"):
    rules_lookup: Dict[str, List[Callable[[CollectionState], bool]]] = {
        "entrances": {
            "To Office Elevator From Underground Blue Tunnels":
                lambda state: state.has("Key for Office Elevator", world.player),
            "To Office Elevator From Office": lambda state: state.has("Key for Office Elevator", world.player),
            "To Bedroom Elevator From Office":
                lambda state: state.has_all({"Key for Bedroom Elevator", "Crawling"}, world.player),
            "To Office From Bedroom Elevator":
                lambda state: state.has_all({"Key for Bedroom Elevator", "Crawling"}, world.player),
            "To Three Floor Elevator From Maintenance Tunnels":
                lambda state: state.has("Key for Three Floor Elevator", world.player),
            "To Three Floor Elevator From Blue Maze Bottom":
                lambda state: state.has("Key for Three Floor Elevator", world.player),
            "To Three Floor Elevator From Blue Maze Top":
                lambda state: state.has("Key for Three Floor Elevator", world.player),
            "To Workshop": lambda state: state.has("Key for Workshop", world.player),
            "To Lobby From Office": lambda state: state.has("Key for Office", world.player),
            "To Office From Lobby": lambda state: state.has("Key for Office", world.player),
            "To Library From Lobby": lambda state: state.has("Key for Library Room", world.player),
            "To Lobby From Library": lambda state: state.has("Key for Library Room", world.player),
            "To Prehistoric From Lobby": lambda state: state.has("Key for Prehistoric Room", world.player),
            "To Lobby From Prehistoric": lambda state: state.has("Key for Prehistoric Room", world.player),
            "To Greenhouse": lambda state: state.has("Key for Greenhouse Room", world.player),
            "To Ocean From Prehistoric": lambda state: state.has("Key for Ocean Room", world.player),
            "To Prehistoric From Ocean": lambda state: state.has("Key for Ocean Room", world.player),
            "To Projector Room": lambda state: state.has("Key for Projector Room", world.player),
            "To Generator": lambda state: state.has("Key for Generator Room", world.player),
            "To Lobby From Egypt": lambda state: state.has("Key for Egypt Room", world.player),
            "To Egypt From Lobby": lambda state: state.has("Key for Egypt Room", world.player),
            "To Janitor Closet": lambda state: state.has("Key for Janitor Closet", world.player),
            "To Shaman From Burial": lambda state: state.has("Key for Shaman Room", world.player),
            "To Burial From Shaman": lambda state: state.has("Key for Shaman Room", world.player),
            "To Inventions From UFO": lambda state: state.has("Key for UFO Room", world.player),
            "To UFO From Inventions": lambda state: state.has("Key for UFO Room", world.player),
            "To Torture From Inventions": lambda state: state.has("Key for Torture Room", world.player),
            "To Inventions From Torture": lambda state: state.has("Key for Torture Room", world.player),
            "To Torture": lambda state: state.has("Key for Puzzle Room", world.player),
            "To Puzzle Room Mastermind From Torture": lambda state: state.has("Key for Puzzle Room", world.player),
            "To Bedroom": lambda state: state.has("Key for Bedroom", world.player),
            "To Underground Lake From Underground Tunnels":
                lambda state: state.has("Key for Underground Lake Room", world.player),
            "To Underground Tunnels From Underground Lake":
                lambda state: state.has("Key for Underground Lake Room", world.player),
            "To Outside From Lobby": lambda state: state.has("Key for Front Door", world.player),
            "To Lobby From Outside": lambda state: state.has("Key for Front Door", world.player),
            "To Maintenance Tunnels From Theater Back Hallways": lambda state: state.has("Crawling", world.player),
            "To Blue Maze From Egypt": lambda state: state.has("Crawling", world.player),
            "To Egypt From Blue Maze": lambda state: state.has("Crawling", world.player),
            "To Lobby From Tar River":
                lambda state: (state.has("Crawling", world.player) and oil_capturable(state, world)),
            "To Tar River From Lobby":
                lambda state: (state.has("Crawling", world.player) and oil_capturable(state, world)
                               and state.can_reach("Tar River", "Region", world.player)),
            "To Burial From Egypt": lambda state: state.can_reach("Egypt", "Region", world.player),
            "To Gods Room From Anansi": lambda state: state.can_reach("Gods Room", "Region", world.player),
            "To Slide Room": lambda state: all_skull_dials_available(state, world),
            "To Lobby From Slide Room": lambda state: (beths_body_available(state, world))
        },
        "locations_required": {
            "Puzzle Solved Anansi Musicbox": lambda state: state.can_reach("Clock Tower", "Region", world.player),
            "Accessible: Storage: Janitor Closet": lambda state: cloth_capturable(state, world),
            "Accessible: Storage: Tar River": lambda state: oil_capturable(state, world),
            "Accessible: Storage: Theater": lambda state: state.can_reach("Projector Room", "Region", world.player),
            "Accessible: Storage: Slide":
                lambda state: beths_body_available(state, world)
                              and state.can_reach("Slide Room", "Region", world.player),
            "Ixupi Captured Water": lambda state: water_capturable(state, world),
            "Ixupi Captured Wax": lambda state: wax_capturable(state, world),
            "Ixupi Captured Ash": lambda state: ash_capturable(state, world),
            "Ixupi Captured Oil": lambda state: oil_capturable(state, world),
            "Ixupi Captured Cloth": lambda state: cloth_capturable(state, world),
            "Ixupi Captured Wood": lambda state: wood_capturable(state, world),
            "Ixupi Captured Crystal": lambda state: crystal_capturable(state, world),
            "Ixupi Captured Sand": lambda state: sand_capturable(state, world),
            "Ixupi Captured Metal": lambda state: metal_capturable(state, world),
            "Final Riddle: Planets Aligned": lambda state: state.can_reach("Fortune Teller", "Region", world.player),
            "Final Riddle: Norse God Stone Message":
                lambda state: (state.can_reach("Fortune Teller", "Region", world.player)
                               and state.can_reach("UFO", "Region", world.player)),
            "Final Riddle: Beth's Body Page 17": lambda state: beths_body_available(state, world),
            "Final Riddle: Guillotine Dropped": lambda state: beths_body_available(state, world),
            "Puzzle Solved Skull Dial Door": lambda state: all_skull_dials_available(state, world),
            },
        "locations_puzzle_hints": {
            "Puzzle Solved Clock Tower Door":
                lambda state: state.can_reach("Three Floor Elevator", "Region", world.player),
            "Puzzle Solved Clock Chains": lambda state: state.can_reach("Bedroom", "Region", world.player),
            "Puzzle Solved Shaman Drums": lambda state: state.can_reach("Clock Tower", "Region", world.player),
            "Puzzle Solved Red Door": lambda state: state.can_reach("Maintenance Tunnels", "Region", world.player),
            "Puzzle Solved UFO Symbols": lambda state: state.can_reach("Library", "Region", world.player),
            "Puzzle Solved Maze Door": lambda state: state.can_reach("Projector Room", "Region", world.player),
            "Puzzle Solved Theater Door": lambda state: state.can_reach("Underground Lake", "Region", world.player),
            "Puzzle Solved Columns of RA": lambda state: state.can_reach("Underground Lake", "Region", world.player),
            "Final Riddle: Guillotine Dropped":
                lambda state: (beths_body_available(state, world)
                               and state.can_reach("Underground Lake", "Region", world.player))
            },
        "elevators": {
            "Puzzle Solved Office Elevator":
                lambda state: ((state.can_reach("Underground Lake", "Region", world.player)
                                or state.can_reach("Office", "Region", world.player))
                               and state.has("Key for Office Elevator", world.player)),
            "Puzzle Solved Bedroom Elevator":
                lambda state: (state.can_reach("Office", "Region", world.player)
                               and state.has_all({"Key for Bedroom Elevator","Crawling"}, world.player)),
            "Puzzle Solved Three Floor Elevator":
                lambda state: ((state.can_reach("Maintenance Tunnels", "Region", world.player)
                                or state.can_reach("Blue Maze", "Region", world.player))
                               and state.has("Key for Three Floor Elevator", world.player))
            },
        "lightning": {
            "Ixupi Captured Lightning": lambda state: lightning_capturable(state, world)
        }
    }
    return rules_lookup


def set_rules(world: "ShiversWorld") -> None:
    multiworld = world.multiworld
    player = world.player

    rules_lookup = get_rules_lookup(world)
    # Set required entrance rules
    for entrance_name, rule in rules_lookup["entrances"].items():
        multiworld.get_entrance(entrance_name, player).access_rule = rule

    # Set required location rules
    for location_name, rule in rules_lookup["locations_required"].items():
        multiworld.get_location(location_name, player).access_rule = rule

    # Set option location rules
    if world.options.puzzle_hints_required.value:
        for location_name, rule in rules_lookup["locations_puzzle_hints"].items():
            multiworld.get_location(location_name, player).access_rule = rule
    if world.options.elevators_stay_solved.value:
        for location_name, rule in rules_lookup["elevators"].items():
            multiworld.get_location(location_name, player).access_rule = rule
    if world.options.early_lightning.value:
        for location_name, rule in rules_lookup["lightning"].items():
            multiworld.get_location(location_name, player).access_rule = rule

    # forbid cloth in janitor closet and oil in tar river
    forbid_item(multiworld.get_location("Accessible: Storage: Janitor Closet", player), "Cloth Pot Bottom DUPE", player)
    forbid_item(multiworld.get_location("Accessible: Storage: Janitor Closet", player), "Cloth Pot Top DUPE", player)
    forbid_item(multiworld.get_location("Accessible: Storage: Tar River", player), "Oil Pot Bottom DUPE", player)
    forbid_item(multiworld.get_location("Accessible: Storage: Tar River", player), "Oil Pot Top DUPE", player)

    # Filler Item Forbids
    forbid_item(multiworld.get_location("Puzzle Solved Lyre", player), "Easier Lyre", player)
    forbid_item(multiworld.get_location("Ixupi Captured Water", player), "Water Always Available in Lobby", player)
    forbid_item(multiworld.get_location("Ixupi Captured Wax", player), "Wax Always Available in Library", player)
    forbid_item(multiworld.get_location("Ixupi Captured Wax", player), "Wax Always Available in Anansi Room", player)
    forbid_item(multiworld.get_location("Ixupi Captured Wax", player), "Wax Always Available in Shaman Room", player)
    forbid_item(multiworld.get_location("Ixupi Captured Ash", player), "Ash Always Available in Office", player)
    forbid_item(multiworld.get_location("Ixupi Captured Ash", player), "Ash Always Available in Burial Room", player)
    forbid_item(multiworld.get_location("Ixupi Captured Oil", player), "Oil Always Available in Prehistoric Room",
                player)
    forbid_item(multiworld.get_location("Ixupi Captured Cloth", player), "Cloth Always Available in Egypt", player)
    forbid_item(multiworld.get_location("Ixupi Captured Cloth", player), "Cloth Always Available in Burial Room",
                player)
    forbid_item(multiworld.get_location("Ixupi Captured Wood", player), "Wood Always Available in Workshop", player)
    forbid_item(multiworld.get_location("Ixupi Captured Wood", player), "Wood Always Available in Blue Maze", player)
    forbid_item(multiworld.get_location("Ixupi Captured Wood", player), "Wood Always Available in Pegasus Room", player)
    forbid_item(multiworld.get_location("Ixupi Captured Wood", player), "Wood Always Available in Gods Room", player)
    forbid_item(multiworld.get_location("Ixupi Captured Crystal", player), "Crystal Always Available in Lobby", player)
    forbid_item(multiworld.get_location("Ixupi Captured Crystal", player), "Crystal Always Available in Ocean", player)
    forbid_item(multiworld.get_location("Ixupi Captured Sand", player), "Sand Always Available in Plants Room", player)
    forbid_item(multiworld.get_location("Ixupi Captured Sand", player), "Sand Always Available in Ocean", player)
    forbid_item(multiworld.get_location("Ixupi Captured Metal", player), "Metal Always Available in Projector Room",
                player)
    forbid_item(multiworld.get_location("Ixupi Captured Metal", player), "Metal Always Available in Bedroom", player)
    forbid_item(multiworld.get_location("Ixupi Captured Metal", player), "Metal Always Available in Prehistoric", player)

    # Set completion condition
    multiworld.completion_condition[player] = lambda state: (first_nine_ixupi_capturable(state, world)
                                                             and lightning_capturable(state, world))




