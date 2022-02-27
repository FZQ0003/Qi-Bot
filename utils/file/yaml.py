import yaml
from . import Config


class YamlConfig(Config):
    suffix: str = 'yml'

    def __init__(self,
                 filename: str,
                 category: str = None):
        super().__init__(filename, category)

    @staticmethod
    def _read_data(text: str) -> dict:
        return yaml.safe_load(text)

    @staticmethod
    def _write_data(data: dict) -> str:
        return yaml.safe_dump(data, sort_keys=False)
