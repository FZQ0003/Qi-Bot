from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from utils.model import QiModel, Field


class BliveEventTypes(str, Enum):
    session_started = 'SessionStarted'
    file_opening = 'FileOpening'
    file_closed = 'FileClosed'
    session_ended = 'SessionEnded'
    stream_started = 'StreamStarted'
    stream_ended = 'StreamEnded'


class BliveEventData(QiModel):
    room_id: int = Field(alias='RoomId')
    short_id: int = Field(alias='ShortId')
    name: str = Field(alias='Name')
    title: str = Field(alias='Title')
    area_name_parent: str = Field(alias='AreaNameParent')
    area_name_child: str = Field(alias='AreaNameChild')
    recording: bool = Field(alias='Recording')
    streaming: bool = Field(alias='Streaming')
    danmaku_connected: bool = Field(alias='DanmakuConnected')
    # session_id: Optional[UUID] = None
    # relative_path: str = Field(alias='RelativePath')
    # file_open_time: datetime = Field(alias='FileOpenTime')
    # file_close_time: datetime = Field(alias='FileCloseTime')
    # file_size: int = Field(alias='FileSize')
    # duration: float = Field(alias='Duration')


class BliveWebhook(QiModel):
    event_type: BliveEventTypes = Field(alias='EventType')
    event_timestamp: datetime = Field(alias='EventTimestamp')
    event_id: UUID = Field(alias='EventId')
    event_data: BliveEventData = Field(alias='EventData')


class BliveMessage(QiModel):
    message: str
    groups: List[int]
    at_all: bool
