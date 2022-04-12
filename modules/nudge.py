from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import NudgeEvent
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from utils.config import bot

channel = Channel.current()

channel.name("Nudge")
channel.description("No description.")
channel.author("F_Qilin")


@channel.use(ListenerSchema(listening_events=[NudgeEvent]))
async def getup(app: Ariadne, event: NudgeEvent):
    if event.supplicant != bot.account and event.target == bot.account:
        if event.context_type == "group":
            await app.sendNudge(event.supplicant, event.group_id)
        elif event.context_type == "friend":
            await app.sendNudge(event.friend_id)
