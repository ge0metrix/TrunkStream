from typing import List, Optional

from pydantic import BaseModel, Field, computed_field, validator

class Word(BaseModel):
    start: float
    end: float
    word: str
    probability: float

class Segment(BaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float
    words: Optional[List[Word]]

class Transcript(BaseModel):
    id: str
    segments: List[Segment]
    transcript: str