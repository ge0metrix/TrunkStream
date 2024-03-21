import logging
import os
import time

from bson import ObjectId
from celery import Celery
from celery.app.log import TaskFormatter
from celery.signals import after_setup_logger
from celery.utils.log import get_task_logger
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

from trunkstream.controllers import transcribe_call
from trunkstream.models import Call
from trunkstream.models.transcript import Transcript

load_dotenv(".env")

uri = os.environ.get("TS_MONGOURL", "")


logger = get_task_logger(__name__)

celery = Celery(__name__)
celery.conf.broker_url = (
    "redis://127.0.0.1:6379/0"  # os.environ.get("CELERY_BROKER_URL")
)
celery.conf.result_backend = (
    "redis://127.0.0.1:6379/0"  # os.environ.get("CELERY_RESULT_BACKEND")
)

celery = Celery(__name__)


@after_setup_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            TaskFormatter(
                "%(asctime)s - %(task_id)s - %(task_name)s - %(name)s - %(levelname)s - %(message)s"
            )
        )


@celery.task(name="create_task")
def create_task(a, b, c):
    time.sleep(a)
    return b + c


@celery.task(
    name="transcribe_call_task",
    autoretry_for=(Exception,),
    retry_backoff=True, 
    retry_kwargs={'max_retries': 3}
)
def transcribe_call_task(callid, filepath) -> str:
    client = MongoClient(uri)
    logger.info(f"Processing call: {callid} - {filepath}")
    db = client.TrunkStream
    collection = db["Calls"]
    call: Call = Call(**collection.find_one({"_id": ObjectId(callid)}))
    transcript = transcribe_call(filepath)
    call.id = callid
    call.transcript = transcript
    collection.update_one(
        {"_id": ObjectId(callid)}, {"$set": {"transcript": transcript.model_dump()}}
    )
    logger.info(f"Finished Processing call: {callid} - {filepath}")
    return transcript.transcript