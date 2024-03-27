"""TODO: TTS config model."""
from ..model import QiModel


class TTSConfigModel(QiModel):
    """Model for Text To Speech (TTS) config."""
    engine: str = 'default'
    access: dict = {}
