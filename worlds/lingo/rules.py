from typing import Optional, List
from BaseClasses import MultiWorld
from .Options import get_option_value
from .static_logic import StaticLingoLogic, RoomAndDoor
from ..AutoWorld import LogicMixin
from ..generic.Rules import set_rule
from .locations import StaticLingoLocations, LocationData
from .player_logic import LingoPlayerLogic, PlayerLocation


class LingoLogic(LogicMixin):
    """
    Logic macros that get reused
    """

    def lingo_can_use_entrance(self, room: str, doors: Optional[List[RoomAndDoor]], world, player, player_logic):
        if doors is None:
            return True
        else:
            for door in doors:
                if self._lingo_can_open_door(room, room if door.room is None else door.room, door.door, world,
                                             player, player_logic):
                    return True
            return False

    def lingo_can_use_pilgrimage(self, player: int, player_logic: LingoPlayerLogic):
        fake_pilgrimage = [
            ["Starting Room", "Main Door"], ["Second Room", "Exit Door"],
            ["Crossroads", "Tower Entrance"], ["Orange Tower Fourth Floor", "Hot Crusts Door"],
            ["Outside The Initiated", "Shortcut to Hub Room"],
            ["Orange Tower First Floor", "Shortcut to Hub Room"],
            ["Outside The Undeterred", "Fours"], ["Hub Room", "Crossroads Entrance"],
            ["The Tenacious", "Shortcut to Hub Room"], ["Outside The Agreeable", "Tenacious Entrance"]
        ]
        viable_option = True
        for entrance in fake_pilgrimage:
            if not self.has(player_logic.ITEM_BY_DOOR[entrance[0]][entrance[1]], player):
                viable_option = False
                break
        return viable_option

    def lingo_can_use_location(self, location: PlayerLocation, room_name: str, world: MultiWorld, player: int,
                               player_logic: LingoPlayerLogic):
        for panel in location.panels:
            panel_room = room_name if panel.room is None else panel.room
            if not self._lingo_can_solve_panel(room_name, panel_room, panel.panel, world, player, player_logic):
                return False
        return True

    def _lingo_can_open_door(self, start_room: str, room: str, door: str, world, player,
                             player_logic: LingoPlayerLogic):
        """
        Determines whether a door can be opened
        """
        if get_option_value(world, player, "shuffle_doors") > 0 and room == "Orange Tower":
            door_object = StaticLingoLogic.DOORS_BY_ROOM[room][door]
            orange_opt = get_option_value(world, player, "orange_tower_access")
            ordered_floors = [
                "Orange Tower - Second Floor",
                "Orange Tower - Third Floor",
                "Orange Tower - Fourth Floor",
                "Orange Tower - Fifth Floor",
                "Orange Tower - Sixth Floor",
                "Orange Tower - Seventh Floor"
            ]
            if orange_opt == 0:  # individual
                return self.has(door_object.item_name, player)
            elif orange_opt == 1:  # vanilla
                for floor in ordered_floors:
                    if not self.has(floor, player):
                        return False
                    if floor == door_object.item_name:
                        break
                return True
            elif orange_opt == 2:  # progressive
                return self.has("Progressive Orange Tower", player, ordered_floors.index(door_object.item_name) + 1)
        else:
            return self.has(player_logic.ITEM_BY_DOOR[room][door], player)

    def _lingo_can_solve_panel(self, start_room: str, room: str, panel: str, world, player,
                               player_logic: LingoPlayerLogic):
        """
        Determines whether a panel can be solved
        """
        if start_room != room and not self.can_reach(room, "Region", player):
            return False
        panel_object = StaticLingoLogic.PANELS_BY_ROOM[room][panel]
        for req_room in panel_object.required_rooms:
            if not self.can_reach(req_room, "Region", player):
                return False
        for req_door in panel_object.required_doors:
            if not self._lingo_can_open_door(start_room, room if req_door.room is None else req_door.room,
                                             req_door.door, world, player, player_logic):
                return False
        if len(panel_object.colors) > 0 and get_option_value(world, player, "shuffle_colors") is True:
            for color in panel_object.colors:
                if not self.has(color.capitalize(), player):
                    return False
        return True


def make_location_lambda(location: PlayerLocation, room_name: str, world: MultiWorld, player: int,
                         player_logic: LingoPlayerLogic):
    return lambda state: state.lingo_can_use_location(location, room_name, world, player, player_logic)


def set_rules(world: MultiWorld, player: int, player_logic: LingoPlayerLogic):
    for room_name, locations in player_logic.LOCATIONS_BY_ROOM.items():
        for location in locations:
            set_rule(world.get_location(location.name, player), make_location_lambda(location, room_name, world, player,
                                                                                     player_logic))