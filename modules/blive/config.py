from enum import Enum
from typing import Dict, List

from utils.file import DefaultConfig
from utils.model import QiModel


class LiveFormat(QiModel):
    start: str = ''
    end: str = ''

    def copy_if_empty(self, copy_form: 'LiveFormat') -> 'LiveFormat':
        start = self.start if self.start else copy_form.start
        end = self.end if self.end else copy_form.end
        return self.__class__(start=start, end=end)


class AtAllLevel(int, Enum):
    never = 0
    only_start = 1
    all = 2


class BliveRoomConfigModel(QiModel):
    enable: bool = True
    format: LiveFormat = LiveFormat()
    name: str = ''
    groups: List[int] = []
    at_all_level: AtAllLevel = AtAllLevel.never


class BliveConfigModel(QiModel):
    rooms: Dict[int, BliveRoomConfigModel] = {}
    format: LiveFormat = LiveFormat(
        start='{name} 直播了！\n{title}\n速来 -> {link}',
        end='{name} 的直播结束了！'
    )


config_file = DefaultConfig('blive')
if not config_file.exists:
    raise ImportError(f'{config_file.path} not found.')
config: BliveConfigModel = config_file.read(BliveConfigModel)
