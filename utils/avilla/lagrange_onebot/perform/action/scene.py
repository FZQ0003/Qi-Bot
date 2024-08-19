from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.profile import NickCapability

if TYPE_CHECKING:
    from avilla.onebot.v11.account import OneBot11Account  # noqa: F401
    from ...protocol import LagrangeOneBotProtocol  # noqa: F401


class LagrangeOnebotActivityActionPerform((m := AccountCollector["LagrangeOneBotProtocol", "OneBot11Account"]())._):
    m.namespace = "avilla.protocol/onebot11-lagrange::action"
    m.identify = "scene"

    @m.entity(NickCapability.set_badge, target="land.group.member")
    async def set_group_member_badge(self, target: Selector, badge: str):
        result = await self.account.connection.call(
            "set_group_special_title",
            {
                "group_id": int(target.pattern["group"]),
                "user_id": int(target.pattern["member"]),
                "special_title": badge
            }
        )
        if result is not None:
            raise RuntimeError(f"Failed to set badge to {target}: {result}")

    @m.entity(NickCapability.unset_badge, target="land.group.member")
    async def unset_group_member_badge(self, target: Selector):
        await self.set_group_member_badge(target, "")
