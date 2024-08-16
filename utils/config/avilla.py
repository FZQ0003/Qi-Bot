"""Avilla (protocol) config models."""
from typing import Literal

from avilla.core import Avilla

from .protocol import ProtocolConfigModel, WebConfigModel
from ..model import field_validator
from ..model.types import QQAccount

__all__ = [
    'AvillaConsoleConfigModel',
    'AvillaElizabethConfigModel',
    'AvillaOnebot11ConfigModel'
]


class AvillaConsoleConfigModel(ProtocolConfigModel):
    """Model for Avilla Console config."""
    protocol: Literal['console'] = 'console'

    def configure(self, app: Avilla) -> None:
        from avilla.console.protocol import ConsoleProtocol
        app.apply_protocols(ConsoleProtocol())


class AvillaElizabethConfigModel(WebConfigModel):
    """Model for Avilla Elizabeth (mirai-api-http) config."""
    protocol: Literal['mirai-api-http', 'elizabeth'] = 'mirai-api-http'
    adapter: Literal['ws'] = 'ws'
    account: list[QQAccount]

    # noinspection PyNestedDecorators
    @field_validator('account', mode='before')
    @classmethod
    def __parse_account(cls, data: int | list[int]) -> list[int]:
        """Parse single account into list."""
        if isinstance(data, int):
            data = [data]
        return data

    def configure(self, app: Avilla) -> None:
        from avilla.elizabeth.protocol import ElizabethProtocol, ElizabethConfig
        app.apply_protocols(protocol := ElizabethProtocol())
        # I don't know why it's designed like that...
        # I can manage multiple accounts in ONE Mirai session!
        for account in self.account:
            protocol.configure(ElizabethConfig(
                qq=account,
                host=self.host,
                port=self.port,
                access_token=self.access_token
            ))


class AvillaOnebot11ConfigModel(WebConfigModel):
    """Model for Avilla Onebot 11 config."""
    protocol: Literal['onebot-11'] = 'onebot-11'
    path: str = '/onebot/v11'

    def configure(self, app: Avilla) -> None:
        from yarl import URL
        from avilla.onebot.v11.protocol import OneBot11Protocol, OneBot11ForwardConfig, OneBot11ReverseConfig
        app.apply_protocols(protocol := OneBot11Protocol())
        if self.adapter == 'ws-reverse':
            protocol.configure(OneBot11ReverseConfig(
                prefix='/',
                path=self.path.split('/ws')[0][1:],  # '/onebot/v11/ws' -> 'onebot/v11'
                endpoint='ws/universal',
                access_token=self.access_token
            ))
        else:
            protocol.configure(OneBot11ForwardConfig(
                endpoint=URL(self.url),
                access_token=self.access_token
            ))
