"""Qi-Bot config."""
from .bot import BotConfigModel

bot_config = BotConfigModel()
"""The bot config must be initialized using load_config()."""


def load_config(path: str = '') -> BotConfigModel:
    """Load and update bot_config.

    Notes:
        Editing returned config will NOT be saved!
    """
    global bot_config

    import platform

    from ..crypto import hash_new
    from ..file import DefaultConfig, Data
    from ..logger import logger

    # Config file
    if (_config_file := DefaultConfig.from_path(path) if path else DefaultConfig(filename='bot')).exists:
        bot_config = _config_file.read(BotConfigModel)
    else:
        logger.warning('Generating config file...')
        # Initialize config
        if (_config_file_example := DefaultConfig(filename='example/bot')).exists:
            bot_config = _config_file_example.read(BotConfigModel)
        else:
            logger.warning(f'Example config file {_config_file_example} not found!')
        _config_file.write(bot_config)

    # HMAC key
    if not bot_config.crypto.hmac.key:
        bot_config.crypto.hmac.key = Data(
            filename='hash_key', suffix='bin', is_bin=True, mode=0o600
        ).executor(
            read=bot_config.crypto.hmac.save_key, write=bot_config.crypto.hmac.save_key
        )(
            lambda header: hash_new(
                f'{header}, {platform.node()}, {platform.processor()}'
            ).digest()
        )('Qi-Bot')

    # Return
    return bot_config
