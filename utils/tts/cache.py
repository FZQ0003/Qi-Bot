from utils.file import AudioCache


class TTSCache(AudioCache):

    def __init__(self, header: str = ''):
        super().__init__(no_init=True, header=header)
