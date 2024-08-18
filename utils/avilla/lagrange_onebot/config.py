from avilla.core import Avilla, BaseProtocol

from utils.config.protocol import update_protocol_types
from ..config.model import AvillaOnebot11ConfigModel


class AvillaLagrangeOneBotConfigModel(AvillaOnebot11ConfigModel):
    """Model for Avilla Lagrange.Onebot config."""

    def configure(self, app: Avilla = ..., protocol: BaseProtocol = ...) -> None:
        from .protocol import LagrangeOneBotProtocol
        if protocol is ...:
            protocol = LagrangeOneBotProtocol()
        super().configure(app, protocol)


update_protocol_types({
    AvillaLagrangeOneBotConfigModel: 10
})
