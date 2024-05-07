import json

from fastapi import UploadFile
from icad_tone_detection import tone_detect

import boto3

from tempfile import NamedTemporaryFile
from ..dbmodels import database
from ..models import *
from .transcribe import *
import os
from dotenv import load_dotenv
import logging
load_dotenv()



logger = logging.getLogger(__name__)


class FileUploadException(Exception):
    pass


def handle_new_call(calljsonfile: UploadFile, audiofile: UploadFile) -> Call:
    calldata = Call(**json.load(calljsonfile.file))
    filepath = f"{calldata.short_name}/{audiofile.filename}"
    url = f"https://trunkstream.s3.amazonaws.com/{filepath}"
    try:

        upload_to_s3(audiofile=audiofile, filename=filepath)

        calldata.filepath = url
        audiofile.file.seek(0)
        logger.info(f"Call Length: {calldata.call_length}")

        inserted = database.collection.insert_one(
            calldata.model_dump(by_alias=True, exclude=["id"])  # type: ignore
        )
        logger.info(
            f"{calldata.talkgroup_tag} - New document _ID: {inserted.inserted_id}"
        )
        newcall: Call = Call(
            **database.collection.find_one({"_id": inserted.inserted_id})
        )
    except Exception as e:
        logger.error(e)
        raise FileUploadException
    return newcall


def upload_to_s3(audiofile: UploadFile, filename: str):
    aws_access_key_id=os.environ.get("AWS_PUBLIC_KEY", None)
    aws_secret_access_key=os.environ.get("AWS_SECRET_KEY", None)
    region_name=os.environ.get("AWS_SREGION", "us-east-1")
    logger.info(f"creds: {aws_access_key_id} - {aws_secret_access_key} - {region_name} - {filename}")
    try:
        temp = NamedTemporaryFile(delete=False)
        audiofile.file.seek(0)
        with temp as f:
            f.write(audiofile.file.read())
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        s3.upload_file(temp.name, "trunkstream", filename)
    except Exception as e:
        logger.error(e)
    finally:
        os.remove(temp.name)