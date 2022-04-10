from .log import _config_warning
from ..file import DefaultConfig
from ..model import QiModel


class FileConfigModel(QiModel):
    cache_enable: bool = True
    newline: bool = True


config_file = DefaultConfig('file')
config: FileConfigModel
if config_file.exists:
    config = config_file.read(FileConfigModel)
else:
    _config_warning(config_file.path)
    config = FileConfigModel()
