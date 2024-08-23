from avilla.core.context import ContextSceneSelector
from avilla.standard.core.account import AccountRegistered
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from utils.avilla.dispatcher import DemoDispatcher, TimeDispatcher

channel = Channel.current()

channel.meta.update(
    name='Init Message',
    description='Send message during init.',
    author=['F_Qilin']
)


@channel.use(ListenerSchema(
    listening_events=[AccountRegistered],
    inline_dispatchers=[DemoDispatcher(), TimeDispatcher()]
))
async def register_msg(scenes: list[ContextSceneSelector], time: str):
    for scene in scenes:
        await scene.send_message(f'[INFO] Account registered at {time}.')
