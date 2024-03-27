"""Protocol config models."""
# from urllib.request import urlopen
from typing import TypeVar, Literal

from ..logger import logger
from ..model import QiModel, Field, field_validator, model_validator, ValidationError
from ..model.types import Host, Port, QQAccount

App = TypeVar('App')


class ProtocolConfigModel(QiModel):
    """Model for custom protocol config."""
    protocol: Literal[''] | str = ''

    def configure(self, app: App) -> None:
        """Activate configuration.

        Notes:
            DO NOT CALL super(), OR YOU WILL SEE A WARNING.
        """
        logger.warning(f'Protocol model "{self.__class__.__name__}" '  # noqa
                       f'neither recognized nor implemented!')


class MiraiHttpConfigModel(ProtocolConfigModel):
    """Model for Mirai HTTP API config."""
    # protocol: Literal['mirai_api_http']
    host: Host
    port: Port
    account: list[QQAccount]
    access_token: str = Field('ServiceVerifyKey', alias='verify_key')

    @property
    def url(self) -> str:
        return f'http://{self.host}:{self.port}'

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def __parse_url(cls, data: dict[str, ...]) -> dict[str, ...]:
        """Parse url into host and port if host is url."""
        if not isinstance(data, dict):
            return data
        host = data.get('host', 'localhost')
        if len((schema_split := host.split('://'))) > 1:
            if (schema := schema_split[0]) not in ['http']:  # ws?
                raise ValidationError(f'URL schema {schema} not supported.')
            host = schema_split[1]
        if len((port_split := host.split(':'))) > 1:
            host = port_split[0]
            try:
                data['port'] = int(port_split[-1].split('/')[0])
            except ValueError:
                data['port'] = data.get('port', 8080)
        data['host'] = host
        return data

    # noinspection PyNestedDecorators
    @field_validator('account', mode='before')
    @classmethod
    def __parse_account(cls, data: int | list[int]) -> list[int]:
        """Parse single account into list."""
        if isinstance(data, int):
            data = [data]
        return data

    # Let the bot framework check!
    # @model_validator(mode='after')
    # def __test_url(self) -> 'MiraiHttpConfigModel':
    #     """Check whether 'http://host:port' is valid."""
    #     code = urlopen(f'http://{self.host}:{self.port}/about').getcode()
    #     if code == 200:
    #         return self
    #     raise ConnectionError(f'URL: {self.host}:{self.port} returned code {code}.')


ProtocolTypes = ProtocolConfigModel | MiraiHttpConfigModel
try:
    from .avilla import AvillaConsoleConfigModel, AvillaElizabethConfigModel
    ProtocolTypes = AvillaConsoleConfigModel | AvillaElizabethConfigModel | ProtocolTypes
except ImportError:
    ...
