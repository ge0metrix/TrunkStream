from datetime import datetime
from typing import Optional, List

from pydantic import validator, BaseModel

class Source(BaseModel):
    id: Optional[int] 
    src: int
    time: datetime
    pos: float
    emergency: bool
    signal_system: str
    tag: str
