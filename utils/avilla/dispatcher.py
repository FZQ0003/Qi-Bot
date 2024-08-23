from datetime import datetime

from avilla.core import Avilla, BaseAccount
from avilla.core.context import Context
from graia.broadcast import BaseDispatcher, DispatcherInterface, ExecutionStop

from utils.stored_data import current

demo = current.bot_config.demo


class DemoDispatcher(BaseDispatcher):
    async def catch(self, interface: DispatcherInterface):
        avilla: Avilla = getattr(interface.event, 'avilla', None)
        account: BaseAccount | None = getattr(interface.event, 'account', None)
        context: Context | None = getattr(interface.event, 'context', None)
        # Get current Avilla for Avilla.current() raises error
        if not avilla:
            for f_dispatcher in interface.broadcast.finale_dispatchers:
                if hasattr(f_dispatcher, 'avilla'):
                    avilla = f_dispatcher.avilla
                    break
        if interface.name == 'scenes':
            if context:
                cxs = [context]
            elif account:
                cxs = [account.get_self_context()]
            else:
                cxs = [_.account.get_self_context() for _ in avilla.accounts.values()]
            return (cx.scene.modify(_) for cx in cxs for _ in demo.get_selectors(cx.land.name))

    async def beforeExecution(self, interface: DispatcherInterface):
        context: Context | None = getattr(interface.event, 'context', None)
        if context and context.scene.pattern not in demo.get_selectors():
            raise ExecutionStop()


class TimeDispatcher(BaseDispatcher):
    # mixin = [BaseDispatcher]
    format: str = '%Y-%m-%d %H:%M:%S'

    async def catch(self, interface: DispatcherInterface):
        if interface.name == 'time' and interface.annotation == str:
            if not (t_format := interface.default):
                t_format = self.format
            return datetime.now().strftime(t_format)
        if interface.annotation == datetime:
            return datetime.now()
