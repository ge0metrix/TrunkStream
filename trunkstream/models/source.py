from datetime import datetime
from typing import Optional, List

from pydantic import validator
from sqlmodel import Field, SQLModel

class Source(SQLModel):
    id: Optional[int] =  Field(default=None, primary_key=True)
    src: int
    time: datetime
    pos: float
    emergency: bool
    signal_system: str
    tag: str
