import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from io import BytesIO
from typing import BinaryIO

from bson import ObjectId
from celery import Celery
from celery.app.log import TaskFormatter
from celery.signals import after_setup_logger
from celery.utils.log import get_task_logger
from dotenv import load_dotenv
from icad_tone_detection import tone_detect
from jinja2 import Template
from pymongo.mongo_client import MongoClient

from trunkstream.controllers import get_call, transcribe_call, update_call
from trunkstream.models import Call, DetectedTones
from trunkstream.models.transcript import Transcript

load_dotenv(".env")

uri = os.environ.get("TS_MONGOURL", "")


smtp_server = os.environ.get("SMTPSERVER", "")
smtp_port: int = int(os.environ.get("SMTPPORT", 25))
smtp_user = os.environ.get("SMTPUSER", "")
smtp_pass = os.environ.get("SMTPPASS", "")
fromemail = os.environ.get("ALERTFROMEMAIL", "")
toemail = os.environ.get("ALERTTOEMAIL", "")

logger = get_task_logger(__name__)


celery = Celery(__name__)


def get_audio_filedata(url) -> BinaryIO:
    data = requests.get(url)
    return BytesIO(data.content)

@after_setup_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            TaskFormatter(
                "%(asctime)s - %(task_name)s[%(task_id)s] - %(name)s - %(levelname)s - %(message)s"
            )
        )


@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    bind=True,
    queue="transcriptions",
)
def transcribe_call_task(self, callid, filepath) -> str:
    try:

        logger.debug(f"Processing call: {callid} - {filepath}")

        if not (call := get_call(callid=callid)):
            raise Exception("Call not found!")
        callaudio = get_audio_filedata(call.filepath)
        transcript = transcribe_call(callaudio)

        updatecommand = {"$set": {"transcript": transcript.model_dump()}}
        if not update_call(callid, updatecommand):
            raise Exception(f"Unable to update call: {callid} with {updatecommand}")

        logger.info(f"Finished Processing call: {callid} - {filepath}")
        x = alert_on_tones.delay(callid=callid)
        return transcript.transcript
    except Exception as e:
        logger.error(e)
        self.retry()
    return ""


@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    bind=True,
    queue="tones",
)
def detect_tones_task(self, callid, filepath):
    logger.debug(f"Detecting Tones for call: {callid} - {filepath}")

    if not (call := get_call(callid)):
        raise Exception("Call not found")

    if call.call_length <= 2:
        return ""

    t = tone_detect(filepath)
    detected = DetectedTones(
        hi_low=t.hi_low_result, quick_call=t.two_tone_result, long=t.long_result
    )
    logger.debug(detected)
    updatecommand = {"$set": {"tones": detected.model_dump()}}
    if not update_call(callid, updatecommand):
        raise Exception(f"Unable to update call: {callid} with {updatecommand}")

    #if detected.has_tones:
    #    x = alert_on_tones.delay(callid=callid)
    #    logger.debug(f"Starting alert thread: {x}")

    return detected.model_dump_json()


def has_transcript(callid) -> bool:

    # query = f"{{'$and': [{{'transcript.transcript': {{'$ne': None}}}}, {{'_id': ObjectId('{callid}')}}]}}"
    # logger.info(query)
    try:
        if not (call := get_call(callid)):
            raise Exception("Call not found!")
        logger.debug(call)
        if call.transcript:
            return True
    except Exception as e:
        logger.error(e)
    return False


@celery.task(queue="tones")
def alert_on_tones(callid: str) -> str:
    x = 0
    MAX_TRIES = 30
    while x < MAX_TRIES:
        time.sleep(10)
        if has_transcript(callid):
            break
        logger.debug(f"{callid} - Has no transcript waiting - Attempt {x}")
        x += 1

    if x == MAX_TRIES:
        logger.error(f"No Transcript avalible for {callid}")
        return f"No Transcript avalible for {callid}"

    logger.debug(f"{callid} Has Transcript")

    if not (call := get_call(callid=callid)):
        raise Exception("Call not found!")

    if not call.tones.has_tones: # type: ignore
        return f"Call: {callid} - Has NO Tones AND Transcript NO ALERT!"

    logger.info(f"Call: {callid} - Has Tones AND Transcript ALERT!")
    x = send_alert_email(callid=callid)
    return f"Call: {callid} - Has Tones AND Transcript ALERT!"


def get_email_html(
    call: Call,
    template_path: str = "trunkstream/templates/toneAlert.html",
) -> str:
    # Read the Jinja2 email template
    with open(template_path, "r") as file:
        template_str = file.read()

    jinja_template = Template(template_str)

    return jinja_template.render(call.model_dump())


@celery.task(queue="tones")
def send_alert_email(callid):
    if not (call := get_call(callid=callid)):
        raise Exception("Call not found!")
    emailhtml = get_email_html(call)
    msg = MIMEMultipart()
    msg["From"] = fromemail
    msg["To"] = toemail
    msg["Subject"] = f"Tones Detected for {call.talkgroup_tag}"
    msg.attach(MIMEText(emailhtml, "html"))
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)
