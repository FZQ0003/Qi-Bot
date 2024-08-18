from avilla.core import Context, ActivityTrigged, Selector
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

channel.meta.update(
    name='Nudge',
    description='No description.',
    author=['F_Qilin']
)


@channel.use(ListenerSchema(listening_events=[ActivityTrigged]))
async def getup(cx: Context, activity: Selector):
    if activity['activity'] == 'nudge':
        accounts = [(_['land'], _['account']) for _ in cx.avilla.accounts]
        sender = cx.endpoint.last_value
        target = cx.client.last_value
        self = cx.self.last_value
        if sender == self and target != self and not (cx.scene['land'], target) in accounts:
            await cx.client.trigger_activity('nudge')  # noqa
