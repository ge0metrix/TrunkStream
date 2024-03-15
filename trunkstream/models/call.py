from datetime import datetime
from typing import Annotated, Optional, List

from pydantic import BeforeValidator, Field, validator, BaseModel, JsonValue

from . import source as _source
from . import frequency as _frequency 
from . import tones as _tones

PyObjectId = Annotated[str, BeforeValidator(str)]

class Call(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    freq: int
    start_time: datetime
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
    freqList: List[_frequency.Frequency]
    srcList: List[_source.Source]
    tones: Optional[List[_tones.DetectedTones]] = None
    transcript: Optional[JsonValue] = None
    filepath: Optional[str] = ""