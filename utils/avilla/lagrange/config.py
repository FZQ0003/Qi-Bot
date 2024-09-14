from typing import Literal

from avilla.core import Avilla, BaseProtocol

from utils.config.protocol import update_protocol_types
from utils.model import field_validator
from utils.model.types import QQAccount, WebURL
from ..config.model import AvillaBaseConfigModel


class AvillaLagrangeConfigModel(AvillaBaseConfigModel):
    """Model for Avilla Lagrange-python config."""
    protocol: Literal['lagrange'] = 'lagrange'
    account: list[QQAccount]
    sign_url: WebURL

    # noinspection PyNestedDecorators
    @field_validator('account', mode='before')
    @classmethod
    def __parse_account(cls, data: int | list[int]) -> list[int]:
        """Parse single account into list."""
        if isinstance(data, int):
            data = [data]
        return data

    def configure(self, app: Avilla = ..., protocol: BaseProtocol = ...) -> None:
        raise NotImplementedError  # TODO: lagrange-python
        # from avilla.lagrange.protocol import LagrangeProtocol
        # from utils.file.base import Data
        # if protocol is ...:
        #     protocol = LagrangeProtocol()
        # super().configure(app, protocol)
        # for account in self.account:
        #     protocol.configure(LagrangeConfig(
        #         uin=account,
        #         protocol='linux',
        #         sign_url=self.sign_url,
        #         device_info_path=Data(
        #             filename=f'{self.protocol}/{account}/device',
        #             suffix='json',
        #             is_bin=False,
        #             mode=0o600
        #         ).path,
        #         sign_info_path=Data(
        #             filename=f'{self.protocol}/{account}/sig',
        #             suffix='bin',
        #             is_bin=True,
        #             mode=0o600
        #         ).path,
        #         cache_path=Data(
        #             filename=f'{self.protocol}/{account}/cache',
        #             suffix='db',
        #             is_bin=True,
        #             mode=0o600
        #         ).path,
        #     ))


update_protocol_types({
    AvillaLagrangeConfigModel: 10
})
