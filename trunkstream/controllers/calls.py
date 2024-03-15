from bson import ObjectId

from ..dbmodels import database
from ..models import *


def get_call(callid: str) -> Call:
    call = database.collection.find_one({"_id": ObjectId(callid)})
    return call


def get_calls(skip: int = 0, limit: int = 10) -> list[Call]:
    calls = database.collection.find().skip(skip).limit(limit=limit)
    return calls
