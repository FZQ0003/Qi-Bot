from typing import Optional
from urllib.request import urlopen

from ..file import DefaultConfig
from ..model import QiModel, validator


class BotConfigModel(QiModel):
    host: str
    account: int
    verify_key: Optional[str] = 'ServiceVerifyKey'
    log: Optional[bool] = False
    modules: Optional[list] = []

    # noinspection PyMethodParameters
    @validator('host')
    def __host(cls, v):
        code = urlopen(v + '/about').getcode()
        if code == 200:
            return v
        raise ConnectionError(f'URL: {v} returned code {code}.')

    # noinspection PyMethodParameters
    @validator('account')
    def __account(cls, v):
        if v < 10000:
            raise ValueError('Invalid QQ number.')
        return v


_config_file = DefaultConfig('bot')
if not _config_file.exists:
    raise FileNotFoundError(f'{_config_file.path} not found.')
_config: BotConfigModel = _config_file.read(BotConfigModel)
