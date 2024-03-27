"""TODO: Web server config model."""
from ..model import QiModel
from ..model.types import Port


class ServerConfigModel(QiModel):
    """Model for internal web server config."""
    enable: bool = False
    port: Port = 5820
