from pathlib import Path
from typing import Union

import pysilk

from . import Cache, DataCheckError, CommonFile


class AudioFile(CommonFile):
    category: str = 'audio'
    suffix: str = 'wav'
    is_elf: bool = True

    def __init__(self, filename: str, suffix: str = None):
        super().__init__(filename, suffix=suffix)

    # TODO: Read & write wave files.


class SilkFile(AudioFile):
    suffix: str = 'slk'

    def to_wav(self) -> AudioFile:
        return AudioFile(self.filename)

    @staticmethod
    def silk_encode(wav_data: bytes) -> bytes:
        return pysilk.encode(wav_data)

    def read_from_wav_file(self, wav_path: Union[str, Path] = None) -> bytes:
        if wav_path is None:
            wav_path = self.to_wav().path_str
        elif isinstance(wav_path, Path):
            wav_path = str(wav_path)
        return pysilk.encode_file(wav_path)

    def write_to_wav(self, data: bytes):
        return self.to_wav().write(pysilk.decode(data, to_wav=True))


# Use silk to save cache
class AudioCache(SilkFile, Cache):

    def __init__(self, filename: str, enable: bool = None):
        super(SilkFile, self).__init__(filename)
        if enable is not None:
            self.enable = enable

    @staticmethod
    def data_check(data: bytes) -> None:
        if len(data) < 512:
            raise DataCheckError('Audio too short!')
