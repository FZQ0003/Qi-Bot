"""Qi-Bot config model."""
from .crypto import CryptoConfigModel
from .file import FileConfigModel
from .protocol import ProtocolTypes
from .shell import ShellConfigModel
from .tts import TTSConfigModel
from .web import ServerConfigModel
from ..file import DefaultConfig
from ..logger import logger
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


if (_config_file := DefaultConfig(filename='bot')).exists:
    bot_config = _config_file.read(BotConfigModel)
else:
    logger.warning('Generating config file...')
    # Initialize config
    if (_config_file_example := DefaultConfig(filename='example/bot')).exists:
        bot_config = _config_file_example.read(BotConfigModel)
    else:
        logger.warning(f'Example config file {_config_file_example} not found!')
        bot_config = BotConfigModel()
    _config_file.write(bot_config)
