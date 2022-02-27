import json
from . import Config


class JsonConfig(Config):
    suffix: str = 'json'

    def __init__(self,
                 filename: str,
                 category: str = None):
        super().__init__(filename, category)

    @staticmethod
    def _read_data(text: str) -> dict:
        return json.loads(text)

    @staticmethod
    def _write_data(data: dict) -> str:
        return json.dumps(data, indent=2)
