import math
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Dict, Tuple, Optional, AnyStr


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
        return math.sqrt((cords1[0] - cords2[0]) ** 2 + (cords1[1] - cords2[1]) ** 2)


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
    time: timedelta


@dataclass
class ResourcesFactor:
    wood: float
    stone: float
    iron: float
    population: float
    time: float


@dataclass
class VillageResources(Resources):
    max_storage: int
    max_population: int

    def get_minimal_materials_count(self):
        return min(self.wood, self.stone, self.iron)

    def is_full_storage(self):
        return self.get_minimal_materials_count() == self.max_storage


@dataclass
class BuildingBaseInfo:
    name: str
    min_level: int
    max_level: int
    base_resources: Resources
    resources_factor: ResourcesFactor
    build_time: float
    build_time_factor: float

    def get_resources_for_level(self, level: int) -> Resources:
        return Resources(
            round(self.base_resources.wood * self.resources_factor.wood ** level),
            round(self.base_resources.stone * self.resources_factor.stone ** level),
            round(self.base_resources.iron * self.resources_factor.iron ** level),
            round(
                self.base_resources.population
                * self.resources_factor.population ** level
                - self.base_resources.population
                * self.resources_factor.population ** (level - 1)
            ),
            self.base_resources.time * self.resources_factor.time ** level,
        )


@dataclass
class VillageBuilding:
    base_info: BuildingBaseInfo
    level: int

    def get_resources_for_next_level(self) -> Resources:
        return self.base_info.get_resources_for_level(self.level + 1)


@dataclass
class OwnedVillage(Village):
    resource_state: VillageResources
    buldings_state: Dict[str, VillageBuilding]


class TroopBuildingTypes(Enum):
    BARRACKS = "barracks"
    STABLE = "stable"
    GARAGE = "garage"


class Buildings(Enum):
    pass
