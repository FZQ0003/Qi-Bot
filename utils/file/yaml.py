import yaml

from . import Config
from ..model import QiModel


class YamlMixin(QiModel):
    suffix: str = 'yml'
    is_elf: bool = False

    @staticmethod
    def reader(source: str) -> dict:
        return yaml.safe_load(source)

    @staticmethod
    def writer(config: dict) -> str:
        return yaml.safe_dump(config, sort_keys=False)


class YamlConfig(YamlMixin, Config):

    def __init__(self, filename: str, category: str = None):
        super().__init__(filename, category)
