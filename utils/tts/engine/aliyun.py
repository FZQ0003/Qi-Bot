import http.client
import json

from utils.config import tts
from utils.online import AcsAccess
from ..cache import TTSCache
from ..engine import TTSEngine

access = AcsAccess(**tts.access)
app_key = tts.access.get('app_key', '')

try:
    assert not access.token.expired
except ConnectionError or AssertionError:
    raise ImportError('Cannot get valid acs token!')


class AliyunTTSEngine(TTSEngine):
    name: str = 'aliyun'
    online: bool = True

    use_default: bool = True

    voice: str = None
    rate: int = None
    pitch: int = None
    volume: int = None

    def __init__(self):
        super().__init__()

    @TTSCache(name)
    def convert(self, text: str, cache: bool = True) -> bytes:
        host = 'nls-gateway.cn-shanghai.aliyuncs.com'
        url = 'https://' + host + '/stream/v1/tts'
        connection = http.client.HTTPSConnection(host)
        connection.request(
            method='POST',
            url=url,
            body=json.dumps({
                'appkey': app_key,
                'token': access.token.id,
                'text': text,
                'format': 'wav',
                'sample_rate': 24000
            }),
            headers={'Content-Type': 'application/json'}
        )
        response = connection.getresponse()
        body = response.read()
        connection.close()
        if response.getheader('Content-Type') == 'audio/mpeg':
            return body
        else:
            raise ConnectionError(f'The POST request failed: {body}')
