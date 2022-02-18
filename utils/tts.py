import subprocess
import time

import pyttsx3
from loguru import logger

from utils.file import AudioCache

LANG = ['zh', 'cmn']


def log_no_specified_voice():
    logger.warning('Language check failed, use default.')


class TTSEngine(object):
    name: str
    online: bool

    def __str__(self):
        return '<{} TTSEngine: {} at {}>'.format(
            'Online' if self.online else 'Offline',
            self.name,
            hex(id(self))
        )

    @property
    def voice(self) -> str:
        raise NotImplementedError

    @voice.setter
    def voice(self, _voice_id: str):
        raise NotImplementedError

    @property
    def rate(self) -> int:
        raise NotImplementedError

    @rate.setter
    def rate(self, _rate: int):
        raise NotImplementedError

    @property
    def pitch(self) -> int:
        raise NotImplementedError

    @pitch.setter
    def pitch(self, _pitch: int):
        raise NotImplementedError

    @property
    def volume(self) -> int:
        raise NotImplementedError

    @volume.setter
    def volume(self, _volume: int):
        raise NotImplementedError

    def convert(self, text: str, cache: bool = True) -> bytes:
        raise NotImplementedError


class OfflineTTSEngine(TTSEngine):
    online: bool = False

    def __init__(self):
        super().__init__()
        self.engine = pyttsx3.init()
        # noinspection PyProtectedMember
        self.name = str(self.engine.proxy._driver.__class__).split('.')[2]
        self.voice_id = None
        for voice in self.engine.getProperty('voices'):  # type: ignore
            # Check languages
            if sum(_ in voice.languages for _ in LANG) > 0:
                self.voice_id = voice.id
                break
        if self.voice_id is None:
            log_no_specified_voice()
        else:
            self.engine.setProperty('voice', self.voice_id)

    @property
    def voice(self) -> str:
        # Why self.engine.getProperty('voice') failed?!
        try:
            return self.engine.getProperty('voice')  # type: ignore
        except KeyError:
            if self.voice_id is None:
                return 'default'
            return self.voice_id

    @voice.setter
    def voice(self, _voice_id: str):
        # No checking methods
        self.engine.setProperty('voice', _voice_id)
        self.voice_id = _voice_id

    @property
    def rate(self) -> int:
        return self.engine.getProperty('rate')  # type: ignore

    @rate.setter
    def rate(self, _rate: int):
        self.engine.setProperty('rate', _rate)

    @property
    def pitch(self) -> int:
        return 50

    @pitch.setter
    def pitch(self, _pitch: int):
        logger.warning('Pitch is not supported in pyttsx3.')

    @property
    def volume(self) -> int:
        return int(self.engine.getProperty('volume') * 100)  # type: ignore

    @volume.setter
    def volume(self, _volume: int):
        self.engine.setProperty('volume', _volume / 100)

    def convert(self, text: str, cache: bool = True) -> bytes:
        cache_file = AudioCache.create(text, enable=cache)

        @cache_file
        def __convert():
            temp_file = cache_file.to_wav()
            self.engine.save_to_file(text, temp_file.path_str)
            self.engine.runAndWait()
            # Wait for about 10 seconds
            i = 0
            while not temp_file.exists:
                i += 1
                if i > 99:
                    raise TimeoutError('Wave file not generated.')
                time.sleep(0.1)
            return cache_file.read_from_wav_file()

        return __convert()


class EspeakNGEngine(TTSEngine):
    name: str = 'espeak-ng'
    online: bool = False

    voice: str = None
    rate: int = 175
    pitch: int = 50
    volume: int = 100

    def __init__(self):
        super().__init__()
        text_voices = subprocess.run(
            [self.name, '--voices'], capture_output=True
        ).stdout.decode()
        for line in text_voices.split('\n'):
            line_split = line.split()
            if sum(_ in line_split for _ in LANG) > 0:
                self.voice = line_split[1]
        if self.voice is None:
            log_no_specified_voice()

    def convert(self, text: str, cache: bool = True) -> bytes:
        # Clear option flags
        while text[0] == '-':
            text = text[1:]

        @AudioCache.create(text, cache)
        def __convert():
            return AudioCache.silk_encode(subprocess.run([
                self.name,
                '' if self.voice is None else f'-v{self.voice}',
                f'-s{self.rate}'
                f'-p{self.pitch}'
                f'-a{self.volume}',
                text, '--stdout'
            ], capture_output=True).stdout)

        return __convert()
