#!/usr/bin/env python3

# Import bot framework
from avilla.core import Avilla

# Import external utilities
from creart import create
from graia.saya import Saya

# Import internal utilities
from utils.config import bot_config, init_config
from utils.config.avilla import AvillaConsoleConfigModel
from utils.logger import logger
from utils.module import get_modules

# TODO: Web (FastAPI)
bot_config.server.enable = False


def main():
    """Main function."""
    # Init
    saya = create(Saya)
    app = Avilla()
    init_config()

    if bot_config.dry_run:
        # For development
        AvillaConsoleConfigModel().configure(app)
    else:
        for protocol_config in bot_config.protocols:
            protocol_config.configure(app)

    # TODO: Web

    # Load modules
    with saya.module_context():  # noqa
        if (modules := bot_config.modules) is None:
            logger.info('Automatically loading modules...')
            modules = get_modules()
        for module_name in modules:
            try:
                saya.require(module_name)
            except ImportError as e:
                logger.error(f'Failed to load {module_name}: {e.msg}')

    # Launch
    app.launch()


if __name__ == '__main__':
    main()
