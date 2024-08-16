import secrets

from fake_data import faker
from utils.config.protocol import WebConfigModel


class TestProtocolConfig:

    def test_web_url(self):
        adapter_mapping = {
            'http': ['http', 'webhook'],
            'ws': ['ws', 'ws-reverse']
        }
        scheme = secrets.choice(list(adapter_mapping.keys()))
        adapter = secrets.choice(adapter_mapping[scheme])
        host = faker.hostname(secrets.randbits(2))
        port = faker.port_number()
        path = '/' + faker.uri_path()
        url = f"{scheme}://{host}:{port}{path}"
        model_1 = WebConfigModel(adapter=adapter, url=url)
        model_2 = WebConfigModel(adapter=adapter, host=host, port=port, path=path)
        assert model_1.adapter == model_2.adapter == adapter
        assert model_1.url == model_2.url == url
        assert model_1.host == model_2.host == host
        assert model_1.port == model_2.port == port
        assert model_1.path == model_2.path == path
