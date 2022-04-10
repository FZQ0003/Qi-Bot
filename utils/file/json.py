import json

from . import Config, ConfigFile, Data
from ..model import QiModel


class JsonMixin(QiModel):
    suffix: str = 'json'
    is_elf: bool = False

    @staticmethod
    def reader(source: str) -> dict:
        return json.loads(source)

    @staticmethod
    def writer(config: dict) -> str:
        return json.dumps(config, indent=2)


class JsonConfig(JsonMixin, Config):

    def __init__(self, filename: str, category: str = None):
        super().__init__(filename, category)


class JsonData(JsonMixin, ConfigFile, Data):

    def __init__(self, filename: str, category: str = None):
        super().__init__(filename, category)

    @staticmethod
    def writer(config: dict) -> str:
        return json.dumps(config, separators=(',', ':'))
