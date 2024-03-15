from typing import List, Optional

from pydantic import BaseModel, Field, computed_field, validator


class ToneBase(BaseModel):
    start: Optional[float]
    end: Optional[float]
    tone_id: str


class HiLowTones(ToneBase):
    tones: List[float] = Field(max_length=2, min_length=2)


class QuickCallTones(ToneBase):
    detected: List[float] = Field(max_length=2, min_length=2)


class LongTone(ToneBase):
    detected: float


class DTMFTone(ToneBase):
    key: str

    @validator("key")
    def valid_dtmf_key(cls, value):
        if value in [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "#",
            "0",
            "*",
            "A",
            "B",
            "C",
            "D",
        ]:
            return value
        raise ValueError("Not a valid DTMF Key")


class DetectedTones(BaseModel):
    # dtmf: List[DTMFTone] = Field(default_factory=list)
    hi_low: List[HiLowTones] = Field(default_factory=list)
    quick_call: List[QuickCallTones] = Field(default_factory=list)
    long: List[LongTone] = Field(default_factory=list)
    
    @computed_field
    @property
    def HasTones(self) -> bool:
        tonecount = len(self.hi_low) + len(self.quick_call) + len(self.long)
        return tonecount > 0