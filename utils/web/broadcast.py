from asyncio import iscoroutinefunction
from functools import wraps
from typing import Any, Callable

from graia.broadcast import (
    BaseDispatcher,
    Broadcast,
    Dispatchable,
    DispatcherInterface,
    Decorator,
    DecoratorInterface,
    ExecutionStop
)

from ..logger import logger
from ..model import QiModel


class Global:
    broadcast: Broadcast = None


class FastAPIMessageEvent(Dispatchable, QiModel):
    type: str = 'FastAPIMessageEvent'

    header: str
    result: Any

    def __init__(self, header: str, result: Any = None):
        super().__init__(header=header, result=result)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface):  # noqa
            if isinstance(interface.event, FastAPIMessageEvent) and interface.name == 'result':
                return interface.event.result


class CheckHeader(Decorator):
    pre = True

    def __init__(self, header: str = ''):
        super().__init__()
        self.header = header

    async def target(self, interface: DecoratorInterface):
        if isinstance(interface.event, FastAPIMessageEvent):
            event: FastAPIMessageEvent = interface.event
            if event.header != self.header and self.header != '':
                raise ExecutionStop
        return interface.return_value


def use_broadcast(header: str,
                  return_result: bool = True,
                  broadcast: Broadcast = None) -> Callable:
    def __func(func: Callable) -> Callable:
        if broadcast is None:
            if Global.broadcast is None:
                logger.error('Broadcast not found, postEvent method disabled.')
                return func
            bcc = Global.broadcast
        else:
            bcc = broadcast

        def __result(result):
            if result is None:
                logger.info(f'{header}: failure')
                return {'event_header': header, 'status': 'failure'}
            bcc.postEvent(FastAPIMessageEvent(header, result))
            logger.info(f'{header}: success')
            if return_result:
                return result
            return {'event_header': header, 'status': 'success'}

        if iscoroutinefunction(func):
            @wraps(func)
            async def __wrapper(*args, **kwargs):
                return __result(await func(*args, **kwargs))
        else:
            @wraps(func)
            def __wrapper(*args, **kwargs):
                return __result(func(*args, **kwargs))

        return __wrapper

    return __func
