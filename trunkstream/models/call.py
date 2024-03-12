from datetime import datetime
from typing import Optional, List

from pydantic import validator
from sqlmodel import Field, SQLModel
from . import source, frequency

class Call(SQLModel):
    id: Optional[int] =  Field(default=None, primary_key=True)
    freq: int
    start_time: datetime = Field(index=True)
    stop_time: datetime
    emergency: bool
    priority: int
    mode: int
    duplex: bool
    encrypted: bool
    call_length: float
    talkgroup: int
    talkgroup_tag: str
    talkgroup_description: str
    talkgroup_group: str
    talkgroup_group_tag: str
    audio_type: str
    short_name: str
    freqList: "List[frequency.Frequency]"
    srcList: "List[source.Source]"

