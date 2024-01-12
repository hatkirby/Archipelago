from BaseClasses import Location
from .static_logic import ALL_REGIONS


class SmsLocation(Location):
    game: str = "Super Mario Sunshine"


ALL_LOCATIONS_TABLE: dict[str, int] = {}

for region in ALL_REGIONS:
    for shine in region.shines:
        ALL_LOCATIONS_TABLE[f"{region.name} - {shine.name}"] = shine.id
