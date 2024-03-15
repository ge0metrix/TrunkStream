from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator


class Frequency(BaseModel):
    freq: int
    time: datetime
    pos: float
    len: float
    error_count: int
    spike_count: int
