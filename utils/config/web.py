from .log import _config_warning
from ..file import DefaultConfig
from ..model import QiModel


class WebConfigModel(QiModel):
    server_port: int = 5820


config_file = DefaultConfig('tts')
config: WebConfigModel
if config_file.exists:
    config = config_file.read(WebConfigModel)
else:
    _config_warning(config_file.path)
    config = WebConfigModel()
