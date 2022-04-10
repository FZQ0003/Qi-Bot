import json
from typing import Any

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from ..file import JsonData, DataCheckError
from ..hash import hash_encode
from ..model import QiModel
from ..string import to_snake
from ..time import get_int_time


class AcsToken(QiModel):
    id: str
    expire_time: int

    @property
    def expired(self) -> bool:
        return self.expire_time < get_int_time() + 10


class AcsTokenData(JsonData):
    category: str = 'aliyun/token'

    def __init__(self, filename: str):
        super().__init__(filename)

    def read(self, target_model=AcsToken) -> Any:
        output: AcsToken = super().read(target_model)
        if output.expired:
            raise DataCheckError('Token expired!')
        return output


class AcsAccess(QiModel):
    id: str
    secret: str

    @property
    def token(self) -> AcsToken:
        token_data = AcsTokenData(hash_encode(self.id))

        @token_data.executor()
        def __token() -> AcsToken:
            client = AcsClient(self.id, self.secret, "cn-shanghai")
            request = CommonRequest()
            request.set_method('POST')
            request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
            request.set_version('2019-02-28')
            request.set_action_name('CreateToken')
            response: bytes = client.do_action_with_exception(request)
            data: dict = json.loads(response)
            if data.get('ErrMsg', ''):
                raise ConnectionError(data)
            token = data['Token']
            return AcsToken(**{to_snake(_): token[_] for _ in token})

        return __token()
