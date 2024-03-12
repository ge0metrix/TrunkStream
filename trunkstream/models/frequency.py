from datetime import datetime
from typing import Optional, List

from pydantic import validator, BaseModel

class Frequency(BaseModel):
    id: Optional[int]
    freq: int
    time: datetime
    pos: float
    len: float
    error_count: int
    spike_count: int