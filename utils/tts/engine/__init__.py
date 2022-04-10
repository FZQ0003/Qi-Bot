__all__ = [
    'TTSEngine',
    'DefaultTTSEngine',
    'EspeakEngine',
    'PyttsxEngine',
    'AliyunTTSEngine'
]

from utils.config import tts
from utils.const import TTS
from utils.logger import logger

LANG = TTS.LANGUAGES


def log_no_specified_voice():
    logger.warning('Language check failed, use default.')


def log_import_error(name: str):
    logger.warning(f'Cannot import {name}.')


class TTSEngine(object):
    name: str
    online: bool

    def __str__(self):
        return '<{} TTSEngine: {} at {}>'.format(
            'Online' if self.online else 'Offline',
            self.name,
            hex(id(self))
        )

    voice: str
    rate: int
    pitch: int
    volume: int

    def convert(self, text: str, cache: bool = True) -> bytes:
        raise NotImplementedError


try:
    from .espeak import EspeakEngine
except ImportError:
    log_import_error('EspeakEngine')
    EspeakEngine = TTSEngine
# try:
#     from .pyttsx import PyttsxEngine
# except ImportError:
#     log_import_error('PyttsxEngine')
#     PyttsxEngine = TTSEngine
# TODO: PyttsxEngine is disabled due to f**king issues.
PyttsxEngine = EspeakEngine
try:
    from .aliyun import AliyunTTSEngine
except ImportError:
    log_import_error('AliyunTTSEngine')
    AliyunTTSEngine = TTSEngine

if tts.engine == 'aliyun':
    DefaultTTSEngine = AliyunTTSEngine
elif tts.engine == 'espeak':
    DefaultTTSEngine = EspeakEngine
else:
    DefaultTTSEngine = TTSEngine
    for engine in EspeakEngine, AliyunTTSEngine, PyttsxEngine:
        if engine is not TTSEngine:
            DefaultTTSEngine = engine
            break
