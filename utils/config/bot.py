"""Qi-Bot config model."""
from .crypto import CryptoConfigModel
from .file import FileConfigModel
from .protocol import ProtocolTypes
from .shell import ShellConfigModel
from .tts import TTSConfigModel
from .web import ServerConfigModel
from ..model import QiModel, field_validator, model_validator
from ..model.types import Module


class BotConfigModel(QiModel):
    """Model for bot config."""
    dry_run: bool = False
    modules: list[Module] | None = None
    protocols: list[ProtocolTypes] = []
    file: FileConfigModel = FileConfigModel()
    shell: ShellConfigModel = ShellConfigModel()
    tts: TTSConfigModel = TTSConfigModel()
    server: ServerConfigModel = ServerConfigModel()
    crypto: CryptoConfigModel = CryptoConfigModel()

    # noinspection PyNestedDecorators
    @field_validator('modules', mode='before')
    @classmethod
    def __parse_modules(cls, data: str | list[str]) -> list[str] | None:
        """Parse a single module string into a list."""
        if isinstance(data, str):
            return None if data == '*' else [data]
        return data

    @model_validator(mode='after')
    def __check_protocol(self) -> 'BotConfigModel':
        """Check protocol config for bot."""
        self.dry_run = len(self.protocols) < 1
        return self
