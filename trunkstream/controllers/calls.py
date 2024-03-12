from ..models import *

def get_call(callid: int) -> Call:
    return mock_call(callid)

def get_calls(skip: int = 0, limit: int = 10) -> list[Call]:
    return [mock_call(x) for x in range(skip, limit)]