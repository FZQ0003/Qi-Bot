from .log import _config_warning
from ..file import DefaultConfig
from ..model import QiModel


class FileConfigModel(QiModel):
    cache_enable: bool = True
    newline: bool = True


_config_file = DefaultConfig('file')
_config: FileConfigModel
if _config_file.exists:
    _config = _config_file.read(FileConfigModel)
else:
    _config_warning(_config_file.path)
    _config = FileConfigModel()
