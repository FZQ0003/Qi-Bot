from typing import Optional

from .log import _config_warning
from ..file import DefaultConfig
from ..model import QiModel


class TTSConfigModel(QiModel):
    engine: str = 'default'
    access: Optional[dict] = {}


config_file = DefaultConfig('tts')
config: TTSConfigModel
if config_file.exists:
    config = config_file.read(TTSConfigModel)
else:
    _config_warning(config_file.path)
    config = TTSConfigModel(engine='espeak')
