from typing import Any
from bson import ObjectId
import pymongo
from ..dbmodels import database
from ..models import *
import logging

logger = logging.getLogger(__name__)

def get_call(callid: str) -> Call | None:
    call = database.collection.find_one({"_id": ObjectId(callid)})
    if call:
        return Call(**call)
    return None


def get_calls(skip: int = 0, limit: int = 10) -> list[Call]:
    calls = list(database.collection.find().sort("start_time",pymongo.DESCENDING).skip(skip).limit(limit=limit))
    return calls


def update_call(callid: str, update: Any) -> bool:
    result = database.collection.update_one({"_id":ObjectId(callid)}, update)
    logger.info(f"Matched: {result.matched_count}\tUpdated: {result.modified_count}")
    if result.matched_count == 1:
        return True
    return False


def get_calls_with_tones(skip:int = 0, limit:int = 100):
    calls = list(database.collection.find({"tones.has_tones":True}).sort("start_time",pymongo.DESCENDING).skip(skip).limit(limit=limit))
    return calls