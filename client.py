import random
import re
import time
from collections import deque
from datetime import timedelta, datetime
from random import uniform
from typing import Tuple
from urllib.parse import urlparse, parse_qs, urlencode

from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from webbot import Browser

from helpers import TimeHelper
from models import Village, WorldSettings, Resources, VillageResources, Troops


def parse_village_html(element: 'WebElement'):
    name_string = element.find_element_by_css_selector('span.village-name').text
    name, x, y = re.match('(.+)\s\((\d+)\|(\d+)\)', name_string).groups()

    village_info_string = element.find_element_by_css_selector('span.village-info').text
    owner, points = re.match('Właściciel:\s(.+)\sPunkty:\s(\d+)', village_info_string).groups()

    village_distance_string = element.find_element_by_css_selector('span.village-distance').text
    distance = re.search('(\d+)\sp', village_distance_string).group(1)
    return Village((int(x), int(y)), int(distance), int(points), name, owner)


class TribalClient:

    def __init__(self, session_cookie, world, word_settings: WorldSettings = None):
        self.driver = Browser()
        self.world = world
        self._session_cookie = session_cookie
        self.barbarians = []
        self.available_troops = {key.value: 0 for key in Troops}

    def login(self):
        self.driver.go_to('https://plemiona.pl')
        self.driver.add_cookie({'name': 'pl_auth', 'value': self._session_cookie})
        self.driver.refresh()
        self.driver.click(text=str(self.world))
        if self.driver.exists(id='popup_box_daily_bonus'):
            self.driver.click(classname='popup_box_close')

    def get_current_domain(self):
        uri = self.driver.get_current_url()
        parsed_uri = urlparse(uri)
        return f'{parsed_uri.scheme}://{parsed_uri.netloc}'

    def get_outgoings_attacks_from_place(self):
        self.go_to_place()
        outgoings_attacks_box = self.driver.driver.find_element_by_id('commands_outgoings')
        attacked_villages_elements = outgoings_attacks_box.find_elements_by_class_name('quickedit-label')

    @staticmethod
    def _replace_screen_in_url(url, screen_name: str) -> str:
        parsed_url = urlparse(url)
        parsed_query = parse_qs(parsed_url.query)
        parsed_query['screen'] = screen_name
        final_url = parsed_url._replace(query=urlencode(parsed_query, doseq=True)).geturl()
        return final_url

    def go_to_place(self):
        if 'screen=place' not in self.driver.get_current_url():
            self.driver.go_to(f'{self.get_current_domain()}/game.php?village=62967&screen=place')

    def go_to_train_screen(self):
        if 'screen=train' not in self.driver.get_current_url():
            self.driver.go_to(f'{self.get_current_domain()}/game.php?village=62967&screen=train')

    def go_to_main_screen(self):
        if 'screen=main' not in self.driver.get_current_url():
            self.driver.go_to(self._replace_screen_in_url(self.driver.get_current_url(), 'main'))

    def slow_type(self, text, *args, **kwargs):
        text_input = self.driver.find_elements(*args, **kwargs)[0]
        text_input.clear()
        for letter in text:
            text_input.send_keys(letter)
            time.sleep(0.020)
            # self.driver.type(letter, *args, clear=False, **kwargs)

    def _extend_viallages_list(self):
        self.driver.driver.find_element_by_css_selector('.village-item.village-more').click()

    def get_nearest_barbarians_villages(self, radius=10):
        # self.go_to_place()
        # self.driver.click(css_selector='input[value="village_name"]')  # nazwa wioski radio button
        self.slow_type('Wioska Barbarzyńska', css_selector='#content_value .target-input-field')
        time.sleep(0.2)
        x = self.driver.driver.find_elements_by_class_name('target-input-field')
        farthest_village_distance = 1
        villages = []
        # time.sleep(0.5)
        while farthest_village_distance < radius:
            time.sleep(0.1)
            villages = self.driver.driver.find_elements_by_css_selector('div.target-select-autocomplete .village-item')[:-1]
            farthest_village_distance = parse_village_html(villages[-1]).distance
            self._extend_viallages_list()
        self.barbarians = []
        for village in villages:
            parsed_village = parse_village_html(village)
            if parsed_village.owner == 'Barbarzyńskie':
                self.barbarians.append(parsed_village)

    def get_troop_type_count_from_place(self, troop_type):
        unparsed_number = self.driver.driver.find_element_by_id(f'units_entry_all_{troop_type}').text
        return int(unparsed_number[1:-1])

    def get_troop_type_count_available_to_recruit(self, troop_type):
        self.go_to_train_screen()
        available_count_element = self.driver.driver.find_element_by_id(f'{troop_type.value}_0_a')
        return int(available_count_element.text[1:-1])

    def get_available_troops(self):
        for troop_type in Troops:
            self.available_troops[troop_type.value] = self.get_troop_type_count_from_place(troop_type)
        return self.available_troops

    def get_available_resources(self) -> Resources:
        wood = int(self.driver.driver.find_element_by_id('wood').text)
        stone = int(self.driver.driver.find_element_by_id('stone').text)
        iron = int(self.driver.driver.find_element_by_id('iron').text)
        max_storage = int(self.driver.driver.find_element_by_id('storage').text)
        population = int(self.driver.driver.find_element_by_css_selector('span#pop_current_label').text)
        max_population = int(self.driver.driver.find_element_by_css_selector('span#pop_max_label').text)
        return VillageResources(wood, stone, iron, population, timedelta(0), max_storage, max_population)

    def _fill_troop_form(self, troop_type, value):
        input_text = self.driver.driver.find_element_by_css_selector(f'#unit_input_{troop_type}')
        input_text.clear()
        input_text.send_keys(value)

    def fill_recruit_troop_form(self, troop_type, value):
        input_element = self.driver.driver.find_element_by_name(troop_type.value)
        input_element.clear()
        input_element.send_keys(str(value))

    def confirm_recruit(self):
        confirm_btn = self.driver.driver.find_element_by_class_name('btn-recruit')
        confirm_btn.click()

    def _fill_target_village_cords(self, cords: Tuple[int, int]):
        target_input = self.driver.driver.find_element_by_class_name('target-input-field')
        target_input.send_keys(f'{cords[0]}{cords[1]}')
        time.sleep(uniform(0.1, 0.2))

    def _confirm_attack(self):
        self.driver.driver.find_element_by_id('target_attack').click()
        time.sleep(uniform(0.1, 0.2))
        self.driver.driver.find_element_by_id('troop_confirm_go').click()

    def send_attack(self, target_cords: Tuple[int, int], troop_config: dict):
        self.go_to_place()
        self._fill_target_village_cords(target_cords)
        for troop_type, troop_count in troop_config.items():
            self._fill_troop_form(troop_type, troop_count)
        self._confirm_attack()

    def send_attack_to_nearest_villages(self, count=5, skip=0, light_chunk_count=5, axe_chunk_count=1):
        self.go_to_place()
        self.get_available_troops()
        count = light_chunk_count + axe_chunk_count
        light_chunk_size = int(self.available_troops[Troops.LIGHT.value] / light_chunk_count)
        axe_chunk_size = int(self.available_troops[Troops.AXE.value] / axe_chunk_count)

        for village in self.barbarians[skip:skip+count]:
            any_troops = False
            if light_chunk_count and light_chunk_size > 10:
                self._fill_troop_form(Troops.LIGHT, light_chunk_size)
                light_chunk_count -= 1
                any_troops = True
            elif axe_chunk_count and axe_chunk_size > 50:
                self._fill_troop_form(Troops.AXE, axe_chunk_size)
                axe_chunk_count -= 1
                any_troops = True
            if any_troops:
                self._fill_target_village_cords(village.cords)
                time.sleep(0.2)
                self._confirm_attack()
                time.sleep(0.2)

    def _get_build_row(self, building_name):
        return self.driver.driver.find_element_by_css_selector(f'tr#main_buildrow_{building_name}')

    def _get_build_orders_rows_for_building(self, building_name: str):
        return self.driver.driver.find_elements_by_class_name(f'buildorder_{building_name}')

    def _get_build_queue_rows(self):
        self.go_to_main_screen()
        return self.driver.driver.find_elements_by_css_selector(
            'tbody#buildqueue>tr.nodrag, tbody#buildqueue>.sortable_row'
        )

    def get_build_queue_size(self):
        return len(self._get_build_queue_rows())

    def get_build_end_time(self):
        build_queue_rows = self._get_build_queue_rows()
        end_time = datetime.now()
        for build_row in build_queue_rows:
            time_string = build_row.find_element_by_css_selector('td')
            end_time += TimeHelper.parse_tribal_timedelta_format(time_string)
        return end_time

    def get_building_level(self, building_name) -> int:
        building_row = self._get_build_row(building_name)
        current_level_string = building_row.find_element_by_tag_name('td').find_element_by_tag_name('span').text
        try:
            current_level = int(re.search("\d+", current_level_string).group())
        except AttributeError:
            current_level = 0
        build_order_row_for_building = self._get_build_orders_rows_for_building(building_name)
        return current_level + len(build_order_row_for_building)

    def build(self, build_queue: deque):
        for i in range(2 - self.get_build_queue_size()):
            if not build_queue:
                print('Pusta kolejka')
                return
            building_name = build_queue.popleft()
            building_row = self._get_build_row(building_name)
            try:
                build_inactive_displayed = building_row.find_element_by_css_selector('span.inactive').is_displayed()
            except NoSuchElementException:
                build_inactive_displayed = False
            if build_inactive_displayed:
                print(f"Currently you can't build {building_name}")
                build_queue.appendleft(building_name)
                return
            build_button = building_row.find_element_by_css_selector('td.build_options a.btn-build')
            try:
                build_button.click()
                level = int(re.search(r'\d+', build_button.text).group())
                print(f'Built {building_name} at level {level}')
                time.sleep(0.1)
            except StaleElementReferenceException:
                build_queue.appendleft(building_name)

    def continous_attack(self, light_chunk_size=20):
        self.go_to_place()
        self.get_available_troops()

        while True:
            if self.get_troop_type_count_from_place(Troops.LIGHT) >= light_chunk_size:
                village = random.choice(self.barbarians)
                self._fill_troop_form(Troops.LIGHT, light_chunk_size)
                time.sleep(0.2)
                self._fill_target_village_cords(village.cords)
                time.sleep(0.2)
                self._confirm_attack()
            else:
                time.sleep(0.2)



# world-select-show-all
