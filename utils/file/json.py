"""JSON (built-in) file manager."""
import json

from . import Config, ConfigFile, Data
from ..model import QiModel


class JsonMixin(QiModel):
    suffix: str = 'json'
    is_bin: bool = False

    @staticmethod
    def loads(string: str) -> dict:
        return json.loads(string)

    @staticmethod
    def dumps(data: dict) -> str:
        return json.dumps(data, indent=2)


class JsonConfig(JsonMixin, Config):
    ...


class JsonData(JsonMixin, ConfigFile, Data):

    @staticmethod
    def dumps(data: dict) -> str:
        return json.dumps(data, separators=(',', ':'))
