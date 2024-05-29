from typing import NamedTuple, List, Dict

from .Regions import postgame_regions


class LocationData(NamedTuple):
    name: str
    region_name: str
    reqs: List[str] = []
    health_cicada: bool = False
    key: bool = False
    big_key: bool = False

    def postgame(self):
        return "Swap upgrade" in self.reqs or self.region_name in postgame_regions


all_locations: List[LocationData] = [
    # 0AC41F72-EE1D-0D32-8F5D-8F25796B6396
    LocationData("Apartment small key chest 1", "Apartment floor 1", ["Combat", "Jump shoes"], key=True),
    # DE415E2A-06EE-83AC-F1A3-5DCA1FA44735
    LocationData("Apartment small key chest 2", "Apartment floor 1", ["Combat", "Jump shoes"], key=True),
    LocationData("Silverfish card chest", "Apartment floor 1", ["Combat", "Jump shoes"]),
    LocationData("Gas guy card chest", "Apartment floor 1 top left", ["Combat", "Jump shoes"]),
    # 5B55A264-3FCD-CF38-175C-141B2D093029
    LocationData("Apartment small key chest 3", "Apartment floor 2", ["Combat", "Jump shoes"], key=True),
    # 2BBF01C8-8267-7E71-5BD4-325001DBC0BA
    LocationData("Apartment small key chest 4", "Apartment floor 3", ["Combat"], key=True),
    LocationData("Watcher card chest", "Apartment floor 3", ["Defeat Watcher"]),
    LocationData("Fisherman card chest", "Beach"),
    LocationData("Cat Statue chest", "Beach", ["Swap upgrade"]),
    LocationData("Blue cube chest", "Beach", ["Swap upgrade"]),
    # 40DE36CF-9238-F8B0-7A57-C6C8CA465CC2
    LocationData("Bedroom small key chest 1", "Bedroom", key=True),
    LocationData("Shieldy card chest", "Bedroom", ["Combat", "Keys:Bedroom:2"]),
    LocationData("Slime card chest", "Bedroom", ["Combat"]),
    LocationData("Seer card chest", "Bedroom", ["Defeat Seer"]),
    # D41F2750-E3C7-BBB4-D650-FAFC190EBD32
    LocationData("Bedroom small key chest 2", "Bedroom", ["Windmill activated"], key=True),
    LocationData("Pew Laser card chest", "Bedroom", ["Windmill activated"]),
    # 401939A4-41BA-E07E-3BA2-DC22513DCC5C
    LocationData("Bedroom small key chest 3", "Bedroom", ["Combat"], key=True),
    LocationData("Broom card chest", "Blank windmill"),
    LocationData("Chaser card chest", "Cell", ["Jump shoes"]),
    LocationData("Torch card chest", "Cell", ["Swap upgrade", "Combat", "Jump shoes"]),
    # 75C2D434-4AE8-BCD0-DBEB-8E6CDA67BF45
    LocationData("Circus small key chest 1", "Circus", ["Combat", "Jump shoes"], key=True),
    LocationData("Contorts card chest", "Circus", ["Combat", "Jump shoes"]),
    LocationData("Fire pillar card chest", "Circus", ["Combat", "Jump shoes"]),
    # 69E8FBD6-2DA3-D25E-446F-6A59AC3E9FC2
    LocationData("Circus small key chest 2", "Circus", ["Combat", "Jump shoes"], key=True),
    # 6A95EB2F-75FD-8649-5E07-3ED37C69A9FB
    LocationData("Circus small key chest 3", "Circus", ["Combat", "Jump shoes"], key=True),
    # A2479A02-9B0D-751F-71A4-DB15C4982DF5
    LocationData("Circus small key chest 4", "Circus", ["Combat", "Jump shoes"], key=True),
    LocationData("Lion card chest", "Circus", ["Combat", "Jump shoes"]),
    LocationData("Arthur and Javiera card chest", "Circus", ["Defeat Servants", "Combat", "Jump shoes"]),
    LocationData("Dog card chest", "Cliff post windmill"),
    LocationData("Rock card chest", "Cliff post windmill"),
    LocationData("Frog card chest", "Crowd floor 2", ["Combat", "Jump shoes"]),
    # BE2FB96B-1D5F-FCD1-3F58-D158DB982C21
    LocationData("Crowd small key chest 1", "Crowd floor 2", ["Combat"], key=True),
    # 5743A883-D209-2518-70D7-869D14925B77
    LocationData("Crowd small key chest 2", "Crowd floor 2", ["Combat", "Jump shoes"], key=True),
    # 21EE2D01-54FB-F145-9464-4C2CC8725EB3
    LocationData("Crowd small key chest 3", "Crowd floor 2", ["Combat", "Jump shoes"], key=True),
    LocationData("Person card chest", "Crowd floor 3", ["Combat", "Jump shoes", "Keys:Crowd:3"]),
    LocationData("The Wall card chest", "Crowd floor 1", ["Defeat The Wall"]),
    LocationData("Extend upgrade chest", "Crowd jump challenge", ["Jump shoes"]),
    # 868736EF-EC8B-74C9-ACAB-B7BC56A44394
    LocationData("Crowd small key chest 4", "Crowd floor 2", ["Combat", "Jump shoes"], key=True),
    LocationData("Intra card chest", "Debug", ["Combat", "Jump shoes"]),
    LocationData("Marina chest", "Debug"),
    LocationData("Melos chest", "Debug"),
    LocationData("Black cube chest", "Debug"),
    LocationData("White cube chest", "Debug", ["Jump shoes"]),
    LocationData("Young card chest", "Drawer", ["Swap upgrade"]),
    LocationData("Carved Rock card chest", "Drawer"),
    LocationData("Miao card chest", "Fields", ["Combat"]),
    LocationData("Mitra card chest", "Fields", ["Combat"]),
    LocationData("Goldman card chest", "Fields", ["Combat"]),
    LocationData("Rank card chest", "Fields", ["Swap upgrade"]),
    LocationData("Fields - Cardboard Box", "Fields"),
    LocationData("Fields - Shopkeeper Trade", "Fields", ["Cardboard Box"]),
    LocationData("Fields - Mitra Trade", "Fields", ["Biking Shoes"]),
    # Hidden path
    LocationData("Spam Can chest", "Fields", ["Swap upgrade"]),
    # Hidden path
    LocationData("Glitch chest", "Fields", ["Swap upgrade"]),
    # Hidden path
    LocationData("Electric Monster chest", "Fields", ["Swap upgrade"]),
    LocationData("Mushroom card chest", "Forest", ["Combat"]),
    # This is the one that takes 2 hours
    LocationData("Green cube chest", "Forest", ["Swap upgrade"]),
    LocationData("Swap upgrade chest", "Go bottom"),
    LocationData("Red cube chest", "Go bottom", ["Swap upgrade"]),
    # 6C8870D4-7600-6FFD-B425-2D951E65E160
    LocationData("Hotel small key chest 1", "Hotel floor 4", ["Combat", "Jump shoes"], key=True),
    LocationData("Dust maid card chest", "Hotel floor 4", ["Combat", "Jump shoes", "Keys:Hotel:1"]),
    LocationData("Dasher card chest", "Hotel floor 3", ["Keys:Hotel:6"]),
    # 64EE884F-EA96-FB09-8A9E-F75ABDB6DC0D
    LocationData("Hotel small key chest 2", "Hotel floor 3", ["Combat"], key=True),
    # 075E6024-FE2D-9C4A-1D2B-D627655FD31A
    LocationData("Hotel small key chest 3", "Hotel floor 3", ["Combat"], key=True),
    LocationData("Burst plant card chest", "Hotel floor 2 right", ["Combat"]),
    # 1990B3A2-DBF8-85DA-C372-ADAFAA75744C
    LocationData("Hotel small key chest 4", "Hotel floor 2 right", key=True),
    # D2392D8D-0633-2640-09FA-4B921720BFC4
    LocationData("Hotel small key chest 5", "Hotel floor 2", ["Combat"], key=True),
    # 019CBC29-3614-9302-6848-DDAEDC7C49E5
    LocationData("Hotel small key chest 6", "Hotel floor 1", key=True),
    # 9D6FDA36-0CC6-BACC-3844-AEFB6C5C6290
    LocationData("Hotel small key chest 7", "Hotel floor 2", ["Jump shoes"], key=True),
    LocationData("Manager card chest", "Hotel floor 1", ["Defeat Manager"]),
    LocationData("City man card chest", "Hotel roof", ["Swap upgrade"]),
    LocationData("Null card chest", "Nexus top", ["Swap upgrade"]),
    LocationData("Edward card chest", "Overworld"),
    LocationData("Annoyer card chest", "Overworld post windmill"),
    LocationData("Slasher card chest", "Red Cave top", ["Combat"]),
    # 72BAD10E-598F-F238-0103-60E1B36F6240
    LocationData("Red Cave small key chest 1", "Red Cave center", key=True),
    # AE87F1D5-57E0-1749-7E1E-1D0BCC1BCAB4
    LocationData("Red Cave small key chest 2", "Red Cave center", ["Combat"], key=True),
    LocationData("Mover card chest", "Red Cave center", ["Keys:Red Cave:6"]),
    LocationData("Rogue card chest", "Red Cave top", ["Defeat Rogue"]),
    # 4A9DC50D-8739-9AD8-2CB1-82ECE29D3B6F
    LocationData("Red Cave small key chest 3", "Red Cave left", ["Combat"], key=True),
    # A7672339-F3FB-C49E-33CE-42A49D7E4533
    LocationData("Red Cave small key chest 4", "Red Cave right", key=True),
    # 83286BFB-FFDA-237E-BA57-CA2E532E1DC7
    LocationData("Red Cave small key chest 5", "Red Cave right", key=True),
    # CDA1FF45-0F88-4855-B0EC-A9B42376C33F
    LocationData("Red Cave small key chest 6", "Red Cave left", ["Combat"], key=True),
    LocationData("Widen upgrade chest", "Red Cave bottom"),
    LocationData("Golden poop chest", "Red Cave Isaac", ["Combat"]),
    LocationData("Walker card chest", "Red Sea"),
    LocationData("Rock creature card chest", "Red Sea", ["Swap upgrade"]),
    LocationData("Suburbian card chest", "Suburb card house"),
    LocationData("Killer card chest", "Suburb", ["Combat", "Swap upgrade"]),
    LocationData("Blue Cube King card chest", "Space"),
    LocationData("Orange Cube King card chest", "Space"),
    LocationData("Triangle NPC card chest", "Space", ["Combat", "Swap upgrade"]),
    # Wiggle glitch available
    LocationData("Heart chest", "Space"),
    # 3307AA58-CCF1-FB0D-1450-5AF0A0C458F7
    LocationData("Street small key chest 1", "Street", ["Combat"], key=True),
    LocationData("Broom chest", "Street"),
    LocationData("Follower card chest", "Street", ["Swap upgrade"]),
    LocationData("Sage card chest", "Terminal"),
    LocationData("Windmill card chest", "Windmill", []),
    LocationData("Windmill - Activation", "Windmill", []),
    LocationData("Golden Broom chest", "Boss Rush", ["Combat"]),
    LocationData("Apartment Health Cicada", "Apartment floor 3", ["Defeat Watcher"], health_cicada=True),
    LocationData("Beach Health Cicada", "Beach", ["Cards:8"], health_cicada=True),
    LocationData("Bedroom Health Cicada", "Bedroom", ["Defeat Seer"], health_cicada=True),
    # Has to be frame 4
    LocationData("Cell Health Cicada", "Cell", ["Cards:24"], health_cicada=True),
    LocationData("Circus Health Cicada", "Circus", ["Defeat Servants"], health_cicada=True),
    LocationData("Crowd Health Cicada", "Crowd floor 1", ["Defeat The Wall"], health_cicada=True),
    LocationData("Hotel Health Cicada", "Hotel floor 1", ["Defeat Manager"], health_cicada=True),
    LocationData("Overworld Health Cicada", "Overworld", ["Combat", "Cards:4"], health_cicada=True),
    LocationData("Red Cave Health Cicada", "Red cave top", ["Defeat Rogue"], health_cicada=True),
    LocationData("Suburb Health Cicada", "Suburb", ["Combat"], health_cicada=True),
    LocationData("Green key item", "Bedroom", ["Defeat Seer"], big_key=True),
    LocationData("Red key item", "Red cave top", ["Defeat Rogue"], big_key=True),
    LocationData("Blue key item", "Crowd floor 1", ["Defeat The Wall"], big_key=True),
]

locations_by_name: Dict[str, LocationData] = {location.name: location for location in all_locations}


def build_locations_by_region_dict():
    result: Dict[str, List[LocationData]] = {}
    for location in all_locations:
        result.setdefault(location.region_name, []).append(location)
    return result


locations_by_region: Dict[str, List[LocationData]] = build_locations_by_region_dict()
