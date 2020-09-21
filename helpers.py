import math
from datetime import timedelta

from models import WorldSettings, Troops
from models import TroopBuildingTypes


def get_troop_speed(troop_type, world_settings: WorldSettings):
    world_speed = getattr(world_settings, 'speed', 1)
    troop_speed = getattr(world_settings, 'troop_speed', 1)
    troop_speed_map = {
        Troops.SPEAR.value: 18,
        Troops.SWORD.value: 22,
        Troops.AXE.value: 18,
        Troops.ARCHER.value: 18,
        Troops.SPY.value: 9,
        Troops.LIGHT.value: 10,
        Troops.MARCHER.value: 10,
        Troops.HEAVY.value: 11,
        Troops.RAM.value: 30,
        Troops.CATAPULT.value: 30,
        Troops.KNIGHT.value: 10,
        Troops.SNOB.value: 35,
    }
    return troop_speed_map[troop_type.value] / world_speed / troop_speed


def get_distance_from_cords(cords1, cords2):
    return math.sqrt((cords1[0] - cords2[0])**2 + (cords1[1] - cords2[1])**2)


def get_troop_types_by_building(building_type):
    building_type = getattr(building_type, 'value', building_type)
    building_to_troops_map = {
        TroopBuildingTypes.BARRACKS.value: [Troops.SPEAR, Troops.SWORD, Troops.AXE, Troops.ARCHER],
        TroopBuildingTypes.STABLE.value: [Troops.SPY, Troops.LIGHT, Troops.HEAVY, Troops.MARCHER],
        TroopBuildingTypes.GARAGE.value: [Troops.SNOB, Troops.CATAPULT]
    }
    return building_to_troops_map[building_type]


class TimeHelper:

    @classmethod
    def parse_tribal_timedelta_format(cls, time_string):
        splitted_time = time_string.text.split(':')
        hours, minutes, seconds = list(map(int, splitted_time))
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
