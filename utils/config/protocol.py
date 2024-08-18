"""Protocol config models."""
from typing import TypeVar, Literal, Union
from urllib.parse import urlparse

from typing_extensions import Self
from ..logger import logger
from ..model import QiModel, model_validator
from ..model.types import Host, Port

# from urllib.request import urlopen

App = TypeVar('App')
Protocol = TypeVar('Protocol')


class ProtocolConfigModel(QiModel):
    """Model for custom protocol config."""
    protocol: Literal[''] | str = ''

    def configure(self, app: App = ..., protocol: Protocol = ...) -> None:
        """Activate configuration.

        Notes:
            DO NOT CALL super(), OR YOU WILL SEE A WARNING.
        """
        logger.warning(f'Protocol model "{self.__class__.__name__}" '  # noqa
                       f'neither recognized nor implemented!')


class WebConfigModel(ProtocolConfigModel):
    """Model for Web-based API config."""
    adapter: Literal['http', 'webhook', 'ws', 'ws-reverse'] = 'ws'
    host: Host = 'localhost'
    port: Port = 8080
    path: str = '/'
    access_token: str = 'ServiceVerifyKey'
    url: str = ''

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def __parse_url(cls, data: dict[str, ...]) -> dict[str, ...]:
        """Parse url into host and port if url is set."""
        if isinstance(data, dict) and (url := data.get('url', '')):
            parse = urlparse(url)
            data_new = {
                'adapter': parse.scheme,
                'host': parse.hostname,
                'port': parse.port,
                'path': parse.path
            }
            for key, value in data_new.items():
                if value and key not in data:
                    data[key] = value
        return data

    @model_validator(mode='after')
    def __set_url(self) -> Self:
        """Parse protocol, host, port and path into url."""
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        protocol = 'ws' if 'ws' in self.adapter else 'http'
        self.url = f'{protocol}://{self.host}:{self.port}{self.path}'
        return self

    # Let the bot framework check!
    # @model_validator(mode='after')
    # def __test_url(self) -> Self:
    #     """Check whether self.url is valid."""
    #     code = urlopen(self.url).getcode()
    #     if code == 200:
    #         return self
    #     raise ConnectionError(f'URL: {self.url} returned code {code}.')


ProtocolTypes: type[Union] = WebConfigModel | ProtocolConfigModel
__model_priority = {
    WebConfigModel: -50,
    ProtocolConfigModel: -100
}


def update_protocol_types(priority: dict[type[ProtocolConfigModel], int]) -> None:
    global __model_priority, ProtocolTypes
    __model_priority.update(priority)
    model_order = sorted(__model_priority.items(), key=lambda _: (-_[1], _[0].__name__))
    ProtocolTypes = Union[tuple(_[0] for _ in model_order)]
