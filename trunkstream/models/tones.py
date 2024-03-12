from typing import List, Optional

from pydantic import validator
from sqlmodel import Field, SQLModel, AutoString, Relationship



class HiLow(SQLModel, table=True):
    __tablename__="hilow_tones" # type: ignore
    actual: tuple[float,float] = Field(sa_type=AutoString)
    id: Optional[int] =  Field(default=None, primary_key=True)
    detectedtoneid: int = Field(foreign_key="detectedtones.id")
    occured: float
    tone_id: str


class QuickCall(SQLModel, table=True):
    __tablename__="quickcall_tones" # type: ignore
    actual: tuple[float,float] = Field(max_length=2, min_length=2, sa_type=AutoString)
    exact: tuple[float,float] = Field(max_length=2, min_length=2, sa_type=AutoString)
    id: Optional[int] =  Field(default=None, primary_key=True)
    detectedtoneid: int = Field(foreign_key="detectedtones.id")
    occured: float
    tone_id: str

class LongTone(SQLModel, table=True):
    __tablename__="long_tones" # type: ignore
    actual: float
    exact: Optional[float] = 0.0
    id: Optional[int] =  Field(default=None, primary_key=True)
    detectedtoneid: int = Field(foreign_key="detectedtones.id")
    occured: float
    tone_id: str

class DTMFTone(SQLModel, table=True):
    __tablename__="dtmf_tones" # type: ignore
    key: str
    id: Optional[int] =  Field(default=None, primary_key=True)
    detectedtoneid: int = Field(foreign_key="detectedtones.id")
    occured: float
    tone_id: str

class DetectedTones(SQLModel, table=True):
    __tablename__="detectedtones" # type: ignore
    id: Optional[int] =  Field(default=None, primary_key=True)
    call_id: int = Field(foreign_key="call.id")
    dtmf: Optional[DTMFTone] = Relationship(back_populates="dtmf_tones")
    hi_low: Optional[HiLow] = Relationship(back_populates="hilow_tones")
    qc: Optional[QuickCall] = Relationship(back_populates="quickcall_tones")
    long: Optional[LongTone] = Relationship(back_populates="long_tones")
