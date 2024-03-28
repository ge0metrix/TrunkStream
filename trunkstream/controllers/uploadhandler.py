import json

from fastapi import UploadFile
from icad_tone_detection import tone_detect

from ..dbmodels import database
from ..models import *
from .transcribe import *
import os
import logging

logger = logging.getLogger(__name__)

class FileUploadException(Exception):
    pass


def handle_new_call(calljsonfile: UploadFile, audiofile: UploadFile) -> Call:
    calldata = Call(**json.load(calljsonfile.file))
    filepath = f"./uploads/{audiofile.filename}"
    try:
        with open(filepath, "wb") as f:
            f.write(audiofile.file.read())
        calldata.filepath = filepath
        audiofile.file.seek(0)
        logger.info(f"Call Length: {calldata.call_length}")

        inserted = database.collection.insert_one(
            calldata.model_dump(by_alias=True, exclude=["id"])  # type: ignore
        )
        logger.info(f"{calldata.talkgroup_tag} - New document _ID: {inserted.inserted_id}")
        newcall: Call = Call(**database.collection.find_one({"_id": inserted.inserted_id}))
    except Exception as e:
        logger.error(e)
        raise FileUploadException
    return newcall
