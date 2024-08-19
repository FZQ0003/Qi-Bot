"""Qi-Bot stored data during runtime."""
from typing import TYPE_CHECKING

from .model import LateInitObject

if TYPE_CHECKING:
    from .config.bot import BotConfigModel


class CurrentDataObject(LateInitObject):
    bot_config: 'BotConfigModel'


current = CurrentDataObject()
