from __future__ import annotations

from avilla.onebot.v11.protocol import OneBot11Protocol
from graia.ryanvk import merge, ref


def _import_performs():
    from .perform.action import activity  # noqa: F401
    from .perform.action import scene  # noqa: F401
    from .perform.action import fixed_file  # noqa: F401
    from .perform.event import fixed_notice  # noqa: F401


class LagrangeOneBotProtocol(OneBot11Protocol):
    _import_performs()
    artifacts = {
        **merge(
            ref("avilla.protocol/onebot11-lagrange::action", "activity"),
            ref("avilla.protocol/onebot11-lagrange::action", "scene"),
            ref("avilla.protocol/onebot11-fixed::action", "file"),
            ref("avilla.protocol/onebot11-fixed::event", "notice"),
            OneBot11Protocol.artifacts
        )
    }
