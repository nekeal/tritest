import math
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional, AnyStr


@dataclass
class Village:
    cords: Tuple[int, int]
    distance: int
    points: int
    name: str
    owner: str

    def get_distance(self, cords):
        cords1 = cords
        cords2 = self.cords
        return math.sqrt((cords1[0] - cords2[0])**2 + (cords1[1] - cords2[1])**2)


@dataclass
class WorldSettings:
    name: Optional[AnyStr]
    speed: float
    troop_speed: float


@dataclass
class Resources:
    wood: int
    stone: int
    iron: int
    population: int
    max_storage: int
    max_population: int

    def get_minimal_materials_count(self):
        return min(self.wood, self.stone, self.iron)

    def is_full_storage(self):
        return self.get_minimal_materials_count() == self.max_storage


class TroopBuildingTypes(Enum):
    BARRACKS = 'barracks'
    STABLE = 'stable'
    GARAGE = 'garage'

class Buildings(Enum):
    pass
