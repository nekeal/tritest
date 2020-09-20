from pathlib import Path
from xml.etree import ElementTree as ET
from xml.etree import ELe

from models import BuildingBaseInfo


class WorldInfoLoader:

    def __init__(self, url: None, filepath: Path):
        self.url = url
        self.filepath = filepath
        self.raw_config = None
    
    def load_raw_config(self):
        self.raw_config = ET.parse(self.filepath).getroot()

    @staticmethod
    def parse_single_building_raw_data(raw_data: ET.Element):
        return BuildingBaseInfo(

        )


    def load(self):
        if self.filepath.exists():
            self.load_raw_config()

