from avilla.core import Context, Notice
from graia.amnesia.message import MessageChain
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.depend import Depend


@Depend
def check_notice(cx: Context, chain: MessageChain):
    if not chain.has(Notice(cx.scene.modify(cx.self.pattern))):
        raise ExecutionStop
