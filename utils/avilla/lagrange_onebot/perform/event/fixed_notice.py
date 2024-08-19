from __future__ import annotations

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.onebot.v11.capability import OneBot11Capability
from avilla.onebot.v11.collector.connection import ConnectionCollector
from avilla.standard.core.activity import ActivityTrigged
from loguru import logger


class OneBot11FixedEventNoticePerform((m := ConnectionCollector())._):
    m.namespace = "avilla.protocol/onebot11-fixed::event"
    m.identify = "notice"

    @m.entity(OneBot11Capability.event_callback, raw_event="notice.notify.poke")
    async def nudge_received(self, raw_event: dict):
        self_id = raw_event["self_id"]
        account = self.connection.accounts.get(self_id)
        if account is None:
            logger.warning(f"Unknown account {self_id} sent message {raw_event}")
            return
        if "group_id" in raw_event:
            group = Selector().land(account.route["land"]).group(str(raw_event["group_id"]))
            target = group.member(str(raw_event["target_id"]))
            operator = group.member(str(raw_event["user_id"]))
            context = Context(account, operator, target, group, group.member(str(self_id)))
            return ActivityTrigged(context, "nudge", group, target.nudge("_"), operator)
        else:
            land = Selector().land(account.route["land"])
            # "sender_id" == "user_id", use "user_id" instead
            target = land.friend(str(raw_event["target_id"]))
            operator = land.friend(str(raw_event["user_id"]))
            friend = operator
            context = Context(account, operator, target, friend, account.route)
            return ActivityTrigged(context, "nudge", friend, target.nudge("_"), operator)
