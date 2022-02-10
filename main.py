import asyncio
import json
from pathlib import Path

from graia.broadcast import Broadcast
from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour


def main():
    """Main function"""

    config_file = 'config.json'
    if not Path(config_file).is_file():
        raise FileNotFoundError(f'{config_file} not found.')

    # Read config.json
    with open(config_file) as f:
        config = json.load(f)  # type: dict

    # Init
    bcc = Broadcast(loop=asyncio.new_event_loop())
    app = Ariadne(
        broadcast=bcc,
        connect_info=MiraiSession(
            host=config['host'],
            verify_key=config['verify_key'],
            account=config['account']
        )
    )
    app.adapter.log = config.get('log', False)

    # Load modules
    saya = Saya(bcc)
    saya.install_behaviours(BroadcastBehaviour(bcc))
    with saya.module_context():
        for module in config.get('modules', []):
            saya.require(module)
        pass

    # Launch
    app.launch_blocking()


if __name__ == '__main__':
    main()
