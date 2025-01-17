import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from io import BytesIO
from typing import BinaryIO, List

from bson import ObjectId
from celery import Celery
from celery.app.log import TaskFormatter
from celery.signals import after_setup_logger
from celery.utils.log import get_task_logger
from dotenv import load_dotenv
from icad_tone_detection import tone_detect
from jinja2 import Template
from pymongo.mongo_client import MongoClient

from trunkstream.controllers import get_calls, transcribe_call, update_call, get_call
from trunkstream.models import Call, DetectedTones
from trunkstream.worker import transcribe_call_task

logger = get_task_logger(__name__)




def main() -> None:
    calllist: List[Call] = get_calls(skip=0, limit=100)
    for x in calllist:
        call: Call = Call(**x)
        if call.transcript is None or call.tones.has_tones:
            print("transcribing call", call.id)
            transcribe_call_task.delay(call.id, call.filepath)
        else:
           print("Transcript already exists", call.id)

if __name__ == "__main__":
    main()