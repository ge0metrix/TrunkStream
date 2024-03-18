from bson import ObjectId
import pymongo
from ..dbmodels import database
from ..models import *


def get_call(callid: str) -> Call | None:
    call = database.collection.find_one({"_id": ObjectId(callid)})
    if call:
        return Call(**call)
    return None


def get_calls(skip: int = 0, limit: int = 10) -> list[Call]:
    calls = list(database.collection.find().sort("start_time",pymongo.DESCENDING).skip(skip).limit(limit=limit))
    return calls
