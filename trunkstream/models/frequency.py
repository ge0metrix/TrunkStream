from datetime import datetime
from typing import Optional, List

from pydantic import validator
from sqlmodel import Field, SQLModel

class Frequency(SQLModel):
    id: Optional[int] =  Field(default=None, primary_key=True)
    freq: int
    time: datetime
    pos: float
    len: float
    error_count: int
    spike_count: int