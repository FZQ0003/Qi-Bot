"""TODO: Qi-Bot file manager."""
# DO NOT CHANGE THE ORDER!
from .error import DataCheckError, _import_warning
from .base import CommonFile, DataFile, ConfigFile, Data, Config
from .cache import CacheFile, Cache
from .json import JsonMixin, JsonConfig, JsonData

# yaml
try:
    from .yaml import YamlMixin, YamlConfig

    DefaultConfig = YamlConfig
except ModuleNotFoundError as e:
    _import_warning(e, 'yaml')
    DefaultConfig = JsonConfig

# pysilk
# try:
#     from .audio import AudioFile, AudioCache
# except ModuleNotFoundError as e:
#     _import_warning(e, 'audio')
