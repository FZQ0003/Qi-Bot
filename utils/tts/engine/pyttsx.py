from pathlib import Path
from time import sleep

import pyttsx3

from utils.logger import logger
from . import TTSEngine, log_no_specified_voice, LANG
from utils.tts.cache import TTSCache


class PyttsxEngine(TTSEngine):
    name: str = 'pyttsx'
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

    @TTSCache(name)
    def convert(self, text: str, cache: bool = True) -> bytes:
        temp_file = Path('.pyttsx-temp')
        self.engine.save_to_file(text, temp_file)
        # TODO: Not execute properly.
        self.engine.runAndWait()
        # Wait for about 10 seconds
        i = 0
        while not temp_file.is_file():
            i += 1
            if i > 99:
                raise TimeoutError('Wave file not generated.')
            sleep(0.1)
        output = temp_file.read_bytes()
        temp_file.unlink()
        return output
