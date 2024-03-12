from datetime import datetime
from typing import Optional, List

from pydantic import validator, BaseModel

class Frequency(BaseModel):
    freq: int
    time: datetime
    pos: float
    len: float
    error_count: int
    spike_count: int