from typing import Union

import pysilk

from . import Cache, DataCheckError, CommonFile


class AudioFile(CommonFile):
    """Silk (V3) File for QQ"""
    category: str = 'audio'
    suffix: str = 'slk'
    is_elf: bool = True

    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)

    def read_from_wav(self) -> bytes:
        wav_path = self.path.with_suffix('.wav')
        return pysilk.encode(wav_path.read_bytes() if wav_path.is_file() else b'')

    def write_to_wav(self, data: bytes) -> int:
        if b'#!SILK_V3' not in data:
            raise DataCheckError('Not a Silk V3 file!')
        wav_path = self.path.with_suffix('.wav')
        if not wav_path.parent.is_dir():
            wav_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        return wav_path.write_bytes(pysilk.decode(data, to_wav=True))


class AudioCache(AudioFile, Cache):

    def __init__(self,
                 filename: str = None,
                 enable: bool = None,
                 no_init: bool = False,
                 header: Union[str, bytes] = b''):
        super().__init__(filename, enable=enable, no_init=no_init, header=header)

    def _exe_end(self, output, input_args: tuple, input_kwargs: dict):
        output = super()._exe_end(output, input_args, input_kwargs)
        if b'#!SILK_V3' not in output:
            output = pysilk.encode(output)
        if len(output) < 512:
            raise DataCheckError('Audio too short!')
        return output
