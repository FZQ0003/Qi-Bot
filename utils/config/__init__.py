"""Qi-Bot config."""
from .bot import BotConfigModel

bot_config = BotConfigModel()
"""The bot config must be initialized using init_config()."""


def init_config():
    """Init bot_config later to avoid partially import error."""
    global bot_config

    import hashlib
    import platform

    from ..file import DefaultConfig, Data
    from ..logger import logger

    # Config file
    if (_config_file := DefaultConfig(filename='bot')).exists:
        bot_config = _config_file.read(BotConfigModel)
    else:
        logger.warning('Generating config file...')
        # Initialize config
        if (_config_file_example := DefaultConfig(filename='example/bot')).exists:
            bot_config = _config_file_example.read(BotConfigModel)
        else:
            logger.warning(f'Example config file {_config_file_example} not found!')
            bot_config = BotConfigModel()
        _config_file.write(bot_config)

    # HMAC key
    if not bot_config.crypto.hmac.key:
        bot_config.crypto.hmac.key = Data(
            filename='hash_key', suffix='bin', is_bin=True
        ).executor(
            read=bot_config.crypto.hmac.save_key, write=bot_config.crypto.hmac.save_key
        )(
            lambda header: hashlib.new(
                bot_config.crypto.hash.algorithm,
                f'{header}, {platform.node()}, {platform.processor()}'.encode()
            ).digest()
        )('Qi-Bot')
