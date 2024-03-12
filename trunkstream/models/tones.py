from typing import List, Optional

from pydantic import validator, BaseModel, Field


class ToneBase(BaseModel):
    occured: float
    tone_id: str

class HiLow(ToneBase):
    actual: List[float] = Field(max_length=2, min_length=2)


class QuickCall(ToneBase):
    actual: List[float] = Field(max_length=2, min_length=2)
    exact: List[float] = Field(max_length=2, min_length=2)


class LongTone(ToneBase):
    actual: float
    exact: Optional[float] = 0.0


class DTMFTone(ToneBase):
    key: str

class DetectedTones(BaseModel):
    dtmf: Optional[DTMFTone]
    hi_low: Optional[HiLow]
    qc: Optional[QuickCall]
    long: Optional[LongTone]
