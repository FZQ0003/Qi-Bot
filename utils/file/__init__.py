from .error import DataCheckError, _import_warning
from .types import CommonFile, DataFile, ConfigFile, Cache, Data, Config

# Must import after .types
from .json import JsonMixin, JsonConfig, JsonData

# pysilk
try:
    from .audio import AudioFile, AudioCache
except ModuleNotFoundError as e:
    _import_warning(e, 'audio')

# yaml
try:
    from .yaml import YamlMixin, YamlConfig

    DefaultConfig = YamlConfig
except ModuleNotFoundError as e:
    _import_warning(e, 'yaml')
    DefaultConfig = JsonConfig
