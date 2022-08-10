from typing import List, Union

from fastapi import Header
from graia.ariadne import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import AtAll
from graia.ariadne.model import Group, MemberPerm
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

# from utils.file import Cache
from utils.web import web_app
from utils.web.broadcast import FastAPIMessageEvent, CheckHeader, use_broadcast
from .config import config, AtAllLevel
from .model import BliveWebhook, BliveEventTypes, BliveMessage

channel = Channel.current()

channel.name("Bilibili Live Reminder")
channel.description("Provide reminder for hosts.")
channel.author("F_Qilin")


@web_app.post('/blive')
@use_broadcast('blive-rec', return_result=False)
def catch_webhook(user_agent: Union[str, None] = Header(default=None),
                  webhook: BliveWebhook = None):
    if user_agent is None or 'BililiveRecorder' not in user_agent or webhook is None:
        return
    data = webhook.event_data
    if webhook.event_type not in (BliveEventTypes.stream_started,
                                  BliveEventTypes.stream_ended):
        return
    if (room := data.room_id) in config.rooms:
        room_config = config.rooms[room]
        if room_config.enable:
            msg_format = room_config.format.copy_if_empty(config.format)
            if webhook.event_type == BliveEventTypes.stream_started:
                format_string = msg_format.start
                at_all = room_config.at_all_level > AtAllLevel.never
            else:
                format_string = msg_format.end
                at_all = room_config.at_all_level > AtAllLevel.only_start
            return BliveMessage(
                message=format_string.format(
                    name=room_config.name if room_config.name else '订阅的UP主',
                    room=room,
                    link=f'https://live.bilibili.com/{room}',
                    title=data.title
                ),
                groups=room_config.groups,
                at_all=at_all
            )


@channel.use(ListenerSchema(
    listening_events=[FastAPIMessageEvent],
    decorators=[CheckHeader('blive-rec')]
))
async def send_live_msg(app: Ariadne, result: BliveMessage):
    group_list: List[Group] = await app.getGroupList()
    msg_at_all = MessageChain([AtAll(), '\n'])
    msg = MessageChain(result.message)
    for group in group_list:
        if group.id in result.groups:
            if result.at_all and group.accountPerm > MemberPerm.Member:
                out_msg = msg_at_all + msg
            else:
                out_msg = msg
            await app.sendMessage(group, out_msg)
