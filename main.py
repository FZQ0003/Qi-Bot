import asyncio
import pkgutil

from graia.ariadne.adapter import DefaultAdapter
from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from loguru import logger

from utils.file import JsonConfig


def main():
    """Main function"""

    # Read config
    config_file = JsonConfig('bot')
    if not config_file.exists:
        raise FileNotFoundError(f'{config_file} not found.')
    config = config_file.read()

    # Init
    bcc = Broadcast(loop=asyncio.new_event_loop())
    app = Ariadne(
        connect_info=DefaultAdapter(
            broadcast=bcc,
            mirai_session=MiraiSession(
                host=config['host'],
                verify_key=config.get('verify_key', None),
                account=config.get('account', None)
            ),
            log=config.get('log', False)
        ),
        disable_logo=True,
        disable_telemetry=True
    )

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
                    module_name = "modules." + module_name
                    try:
                        saya.require(module_name)
                    except ImportError:
                        logger.error(f'Failed to require {module_name}.')

    # Launch
    app.launch_blocking()


if __name__ == '__main__':
    main()
