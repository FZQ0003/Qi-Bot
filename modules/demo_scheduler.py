from avilla.core.context import ContextSceneSelector
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

from utils.avilla.dispatcher import DemoDispatcher, TimeDispatcher

channel = Channel.current()

channel.meta.update(
    name='Scheduled Message',
    description='Send message regularly.',
    author=['F_Qilin']
)


@channel.use(SchedulerSchema(
    timer=timers.every_hours(),
    dispatchers=[DemoDispatcher(), TimeDispatcher()]
))
async def scheduled_message(scenes: list[ContextSceneSelector], time: str):
    for scene in scenes:
        await scene.send_message(f'[INFO] Now: {time}')
