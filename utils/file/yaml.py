"""YAML (third-party) file manager."""
import yaml

from . import Config, ConfigFile, Data
from ..model import QiModel


class YamlMixin(QiModel):
    suffix: str = '.yml'
    is_bin: bool = False

    @staticmethod
    def loads(string: str) -> dict:
        return yaml.safe_load(string)

    @staticmethod
    def dumps(data: dict) -> str:
        return yaml.safe_dump(data, sort_keys=False)


class YamlConfig(YamlMixin, Config):
    ...


class YamlData(YamlMixin, ConfigFile, Data):
    # TODO: YamlData?
    ...
