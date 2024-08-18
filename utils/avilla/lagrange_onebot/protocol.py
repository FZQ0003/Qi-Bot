from __future__ import annotations

from avilla.onebot.v11.protocol import OneBot11Protocol
from graia.ryanvk import merge, ref


def _import_performs():
    from .perform.action import activity  # noqa: F401


class LagrangeOneBotProtocol(OneBot11Protocol):
    _import_performs()
    artifacts = {
        **merge(
            ref("avilla.protocol/onebot11-lagrange::action", "activity"),
            OneBot11Protocol.artifacts
        )
    }
