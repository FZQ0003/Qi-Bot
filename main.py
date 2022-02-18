import asyncio
import json
import pkgutil
import sys

from pathlib import Path
from loguru import logger

from graia.broadcast import Broadcast
from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour


def main():
    """Main function"""

    # Read args
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = 'config/bot.json'

    # Read config
    if not Path(config_file).is_file():
        raise FileNotFoundError(f'{config_file} not found.')
    with open(config_file) as f:
        config = json.load(f)  # type: dict

    # Init
    bcc = Broadcast(loop=asyncio.new_event_loop())
    app = Ariadne(
        broadcast=bcc,
        connect_info=MiraiSession(
            host=config['host'],
            verify_key=config.get('verify_key', None),
            account=config['account']
        )
    )
    app.adapter.log = config.get('log', False)

    # Load modules
    # noinspection SpellCheckingInspection
    saya = Saya(bcc)
    saya.install_behaviours(BroadcastBehaviour(bcc))
    with saya.module_context():
        modules = config.get('modules', [])
        if modules:
            for module in modules:
                saya.require(module)
        else:
            logger.warning('No module loaded. Use auto mode...')
            for module_info in pkgutil.iter_modules(["modules"]):
                module_name = module_info.name
                if not module_name.startswith("_"):
                    saya.require("modules." + module_name)

    # Launch
    app.launch_blocking()


if __name__ == '__main__':
    main()
