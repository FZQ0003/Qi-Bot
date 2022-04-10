import subprocess

from . import TTSEngine, log_no_specified_voice, LANG
from ..cache import TTSCache


def __test(cmd: str) -> bool:
    return subprocess.run(
        f'{cmd} --version',
        capture_output=True,
        shell=True
    ).returncode == 0


if __test('espeak-ng'):
    ESPEAK_NAME = 'espeak-ng'
elif __test('espeak'):
    ESPEAK_NAME = 'espeak'
else:
    raise ImportError('Espeak (espeak-ng/espeak) not installed!')


class EspeakEngine(TTSEngine):
    name: str = ESPEAK_NAME
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

    @TTSCache(name)
    def convert(self, text: str, cache: bool = True) -> bytes:
        # Clear option flags
        while text[0] == '-':
            text = text[1:]
        return subprocess.run([
            self.name,
            '' if self.voice is None else f'-v{self.voice}',
            f'-s{self.rate}'
            f'-p{self.pitch}'
            f'-a{self.volume}',
            text, '--stdout'
        ], capture_output=True).stdout
