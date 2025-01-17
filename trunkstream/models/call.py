from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Annotated, Dict, List, Optional, Self

from pydantic import BaseModel, BeforeValidator, Field, JsonValue, validator, computed_field, model_validator

from . import frequency as _frequency
from . import source as _source
from . import tones as _tones
from . import transcript as _transcript

import logging

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
    tones: Optional[_tones.DetectedTones] = _tones.DetectedTones()
    transcript: Optional[_transcript.Transcript] = None
    filepath: Optional[str] = ""
    start_time_local: Optional[datetime] = None

    @model_validator(mode="after")
    def local_datetime (self) -> Self:
        if isinstance(self.start_time, datetime):
            self.start_time = self.start_time.replace(tzinfo=timezone.utc)
            logging.debug(self.start_time)
            self.start_time_local = self.start_time.astimezone(ZoneInfo('America/New_York'))
            logging.debug(self.start_time_local)

        return self