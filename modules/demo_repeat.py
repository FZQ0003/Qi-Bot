from avilla.core import Context, MessageReceived, Message
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from utils.avilla.decorator import check_notice
from utils.avilla.dispatcher import DemoDispatcher

channel = Channel.current()

channel.meta.update(
    name='Repeat ME!',
    description='Repeat whatever you say (in text).',
    author=['F_Qilin']
)


@channel.use(ListenerSchema(
    listening_events=[MessageReceived],
    inline_dispatchers=[DemoDispatcher()],
    decorators=[check_notice]
))
async def repeat(cx: Context, msg: Message):
    await cx.scene.send_message('[REPEAT] ' + str(msg.content), reply=msg)
