"""Avilla (protocol) config models."""
from typing import Literal

from avilla.core import Avilla

from .protocol import ProtocolConfigModel, MiraiHttpConfigModel


class AvillaConsoleConfigModel(ProtocolConfigModel):
    """Model for Avilla Console config."""
    protocol: Literal['console'] = 'console'

    def configure(self, app: Avilla) -> None:
        from avilla.console.protocol import ConsoleProtocol
        app.apply_protocols(ConsoleProtocol())


class AvillaElizabethConfigModel(MiraiHttpConfigModel):
    """Model for Avilla Elizabeth (mirai-api-http) config."""
    protocol: Literal['mirai_api_http', 'elizabeth'] = 'mirai_api_http'

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
