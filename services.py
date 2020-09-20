import random
from datetime import timedelta, datetime
from enum import Enum
from typing import List

from selenium.common.exceptions import NoSuchElementException

from client import TribalClient, Troops
from helpers import get_distance_from_cords, get_troop_speed, get_troop_types_by_building
from models import Village, WorldSettings, TroopBuildingTypes

farm_strategies = ('closest', 'random', 'continous')

troop_building_types = ('barracks', 'stable', 'garage',)


def farm_villages(client: TribalClient, villages: List[Village], strategy='closest', village_count=2,
                  skip_count=0,
                  light_chunk_size=10,
                  spear_chunk_size=10,
                  sword_chunk_size=10,
                  stop_at_full_storage=True):
    client.go_to_place()
    if strategy == 'closest':
        villages = sorted(villages, key=lambda v: v.distance)[skip_count:skip_count + village_count]
        loop_length = len(villages)*20

    elif strategy == 'random':
        loop_length = village_count

    for i in range(loop_length):
        if stop_at_full_storage and client.get_available_resources().is_full_storage():
            return
        if strategy == 'random':
            village = random.choice(villages)
        elif strategy == 'closest':
            village = villages[i % village_count]
        available_troops = client.get_available_troops()
        troops_to_attack = {}
        if hasattr(Troops, 'KNIGHT'):
            troops_to_attack[Troops.KNIGHT.value] = available_troops[Troops.KNIGHT.value]
        if available_troops[Troops.LIGHT.value] >= light_chunk_size:
            troops_to_attack[Troops.LIGHT.value] = light_chunk_size
            client.send_attack(village.cords, troop_config=troops_to_attack)
        elif available_troops[Troops.SPEAR.value] >= spear_chunk_size:
            troops_to_attack[Troops.SPEAR.value] = spear_chunk_size
            client.send_attack(village.cords, troop_config=troops_to_attack)
        elif available_troops[Troops.SWORD.value] >= sword_chunk_size:
            troops_to_attack[Troops.SWORD.value] = sword_chunk_size
            client.send_attack(village.cords, troop_config=troops_to_attack)


def get_trip_time_for_all_units_between_cords(cords1, cords2, world_settings: WorldSettings):
    distance = get_distance_from_cords(cords1, cords2)
    trip_times_per_troop = {}
    for troop_type in Troops:
        troop_speed = get_troop_speed(troop_type, world_settings)
        trip_time = distance * troop_speed * 60
        trip_times_per_troop[troop_type] = trip_time
    return trip_times_per_troop


def show_trip_time_for_all_units_between_cords(cords1, cords2, world_settings: WorldSettings):
    trip_times_per_troop = get_trip_time_for_all_units_between_cords(cords1, cords2, world_settings)

    for troop_type, total_time in trip_times_per_troop.items():
        print(f"{troop_type.value}, TIME: {round(total_time)} {str(timedelta(seconds=round(total_time)))}")


def get_recruit_end_times(client: TribalClient):
    client.go_to_train_screen()
    recruit_end_times = {}
    for troop_building_type in TroopBuildingTypes:
        try:
            troop_building_type_recruit_box = client.driver.driver. \
                                               find_element_by_id(f'trainqueue_wrap_{troop_building_type.value}'). \
                                               find_elements_by_css_selector('tr.lit,tr.sortable_row')
        except NoSuchElementException:
            print(f"Cant get {troop_building_type.value} queue")
            troop_building_type_recruit_box = []
        total_time = timedelta()
        for row in troop_building_type_recruit_box:
            time_td = row.find_elements_by_tag_name('td')[1]
            splitted_time = time_td.text.split(':')
            hours, minutes, seconds = list(map(int, splitted_time))
            recruit_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            total_time += recruit_time
        recruit_end_times[troop_building_type.value] = datetime.now() + total_time
    return {k: v for k, v in sorted(recruit_end_times.items(), key=lambda item: item[1])}


def recruit_by_relative_value(client: TribalClient, troop_relative_recruit_config: dict):
    recruit_end_times = get_recruit_end_times(client)
    for building_type in recruit_end_times.keys():
        for troop_type in get_troop_types_by_building(building_type):
            relative_value = troop_relative_recruit_config.get(troop_type.value)
            if relative_value:
                max_count = client.get_troop_type_count_available_to_recruit(troop_type)
                client.fill_recruit_troop_form(troop_type, round(max_count * relative_value))
    client.confirm_recruit()
# .find_elements_by_tag_name('td')[1].text

