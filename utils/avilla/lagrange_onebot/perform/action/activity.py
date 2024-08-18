from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.activity import ActivityTrigger

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account  # noqa: F401
    from ...protocol import LagrangeOneBotProtocol  # noqa: F401


class LagrangeOnebotActivityActionPerform((m := AccountCollector["LagrangeOneBotProtocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11-lagrange::action"
    m.identify = "activity"

    @m.entity(ActivityTrigger.trigger, target="land.friend.activity(nudge)")
    async def friend_nudge(self, target: Selector):
        await self.account.connection.call(
            "friend_poke",
            {
                "user_id": int(target["friend"])
            }
        )

    @m.entity(ActivityTrigger.trigger, target="land.group.member.activity(nudge)")
    async def group_nudge(self, target: Selector):
        await self.account.connection.call(
            "group_poke",
            {
                "group_id": int(target["group"]),
                "user_id": int(target["member"])
            }
        )
