import asyncio

from arclet.alconna import Alconna, Args, AllParam, Arpamar
from arclet.alconna.graia import AlconnaDispatcher
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Voice, Source
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from utils.file import DataCheckError
from utils.tts.engine import AliyunTTSEngine

channel = Channel.current()

channel.name("TTS")
channel.description("Provide Text To Speech ability for the bot.")
channel.author("F_Qilin")

command = Alconna(
    headers=['/'],
    command='tts',
    main_args=Args['text': AllParam]
)
engine = AliyunTTSEngine()


def convert_text(text):
    return Voice(data_bytes=engine.convert(text))


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[AlconnaDispatcher(alconna=command)]
))
async def tts_group_listener(app: Ariadne,
                             group: Group,
                             message: MessageChain,
                             result: Arpamar):
    text: str = result.main_args['text'][0]
    if len(text) == 0:
        return
    try:
        audio = await asyncio.get_running_loop().run_in_executor(
            None, convert_text, text
        )
        await app.sendMessage(group, MessageChain([audio]))
    except DataCheckError:
        await app.sendMessage(group,
                              MessageChain('???'),
                              quote=message.getFirst(Source))
