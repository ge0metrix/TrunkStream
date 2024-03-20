import os
import time

from celery import Celery
from dotenv import load_dotenv
from trunkstream.controllers import transcribe_call
from trunkstream.models.transcript import Transcript
from trunkstream.models import Call
from trunkstream.dbmodels.database import collection
from bson import ObjectId
load_dotenv(".env")

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")

celery = Celery(__name__)

@celery.task(name="create_task")
def create_task(a, b, c):
    time.sleep(a)
    return b + c


@celery.task(name="transcribe_call_task", )
def transcribe_call_task(callid, filepath) -> str:
    call: Call = Call(**collection.find_one({"_id":ObjectId(callid)}))
    transcript = transcribe_call(filepath)
    call.id = callid
    call.transcript = transcript
    collection.update_one({"_id":ObjectId(callid)}, {'$set':{"transcript":transcript}})
    return call.model_dump_json()
