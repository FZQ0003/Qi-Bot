from pathlib import Path
from typing import Union, List

from .log import _config_warning
from ..file import DefaultConfig
from ..model import QiModel, validator


class ShellConfigModel(QiModel):
    timeout: Union[int, float] = 30
    shell_exec: Union[List[str], str] = ['bash']
    check_dir: str = 'tmp/shell'

    # noinspection PyMethodParameters
    @validator('timeout')
    def __timeout(cls, v):
        return v if v > 5 else 5

    # noinspection PyMethodParameters
    @validator('shell_exec')
    def __shell_exec(cls, v):
        if isinstance(v, str):
            return v.split(' ')
        return v


config_file = DefaultConfig('shell')
config: ShellConfigModel
if config_file.exists:
    config = config_file.read(ShellConfigModel)
else:
    _config_warning(config_file.path)
    config = ShellConfigModel()
