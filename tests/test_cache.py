import secrets

from utils.config import bot_config
from utils.file import CacheFile


class SampleCache(CacheFile):
    prefix: str = 'tmp'
    category: str = 'test'


class TestCache:

    @SampleCache(
        suffix='.bin', is_bin=True, enable=True,
        no_name=True, header=secrets.token_bytes(), read_args=[1, 'arg_1']
    )
    def sample_func(self, arg_1: bytes, arg_2: bytes) -> bytes:
        return arg_1 + arg_2 + secrets.token_bytes()

    def test_cache(self):
        arg_1 = secrets.token_bytes()
        arg_2 = secrets.token_bytes()
        output: bytes = self.sample_func(arg_1, arg_2)  # noqa
        assert output.startswith(arg_1 + arg_2)
        assert output == self.sample_func(arg_1, secrets.token_bytes())  # noqa

    def test_cache_config(self):
        assert SampleCache().enable == bot_config.file.cache.enable
        bot_config.file.cache.enable = not bot_config.file.cache.enable
        assert SampleCache().enable == bot_config.file.cache.enable
