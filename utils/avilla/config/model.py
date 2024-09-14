"""Avilla (protocol) config models."""
from typing import Literal

from avilla.core import Avilla, BaseProtocol

from utils.config.protocol import ProtocolConfigModel, WebConfigModel, update_protocol_types
from utils.model import field_validator
from utils.model.types import QQAccount


class AvillaBaseConfigModel(ProtocolConfigModel):
    def configure(self, app: Avilla = ..., protocol: BaseProtocol = ...) -> None:
        if app is ... or protocol is ...:
            super().configure()
        else:
            app.apply_protocols(protocol)


class AvillaConsoleConfigModel(AvillaBaseConfigModel):
    """Model for Avilla Console config."""
    protocol: Literal['console'] = 'console'

    def configure(self, app: Avilla = ..., protocol: BaseProtocol = ...) -> None:
        from avilla.console.protocol import ConsoleProtocol
        if protocol is ...:
            protocol = ConsoleProtocol()
        super().configure(app, protocol)


class AvillaElizabethConfigModel(AvillaBaseConfigModel, WebConfigModel):
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

    def configure(self, app: Avilla = ..., protocol: BaseProtocol = ...) -> None:
        from avilla.elizabeth.protocol import ElizabethProtocol, ElizabethConfig
        if protocol is ...:
            protocol = ElizabethProtocol()
        super().configure(app, protocol)
        # I don't know why it's designed like that...
        # I can manage multiple accounts in ONE Mirai session!
        for account in self.account:
            protocol.configure(ElizabethConfig(
                qq=account,
                host=self.host,
                port=self.port,
                access_token=self.access_token
            ))


class AvillaOnebot11ConfigModel(AvillaBaseConfigModel, WebConfigModel):
    """Model for Avilla Onebot 11 config."""
    protocol: Literal['onebot-11'] = 'onebot-11'
    path: str = '/onebot/v11'

    def configure(self, app: Avilla = ..., protocol: BaseProtocol = ...) -> None:
        from yarl import URL
        from avilla.onebot.v11.protocol import OneBot11Protocol, OneBot11ForwardConfig, OneBot11ReverseConfig
        if protocol is ...:
            protocol = OneBot11Protocol()
        super().configure(app, protocol)
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


update_protocol_types({
    AvillaBaseConfigModel: -10,
    AvillaConsoleConfigModel: 0,
    AvillaElizabethConfigModel: 0,
    AvillaOnebot11ConfigModel: 0
})
