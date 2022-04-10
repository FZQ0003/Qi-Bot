from typing import Optional

from .log import _config_warning
from ..file import DefaultConfig
from ..model import QiModel


class TTSConfigModel(QiModel):
    engine: str = 'default'
    access: Optional[dict] = {}


_config_file = DefaultConfig('tts')
_config: TTSConfigModel
if _config_file.exists:
    _config = _config_file.read(TTSConfigModel)
else:
    _config_warning(_config_file.path)
    _config = TTSConfigModel(engine='espeak')
