from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator


class Source(BaseModel):
    src: int
    time: datetime
    pos: float
    emergency: bool
    signal_system: str
    tag: str
