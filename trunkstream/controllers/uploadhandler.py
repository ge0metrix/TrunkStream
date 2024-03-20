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
        try: 
            if calldata.call_length > 2:
                t = tone_detect(audiofile.file)
                detected = DetectedTones(
                    hi_low=t.hi_low_result, quick_call=t.two_tone_result, long=t.long_result
                )
                calldata.tones = detected
                if calldata.tones.has_tones:
                    logger.warn(f"Tones detected: {calldata.tones}")
                else:
                    logger.info(f"No tones detected: {calldata.tones}")

                #ts = transcribe_call(callaudio=filepath)
                #calldata.transcript=ts
            else:
                logger.warn(f"Call Too Short: {calldata.call_length}")
                
        except ValueError as e:
            logger.error(e)

        inserted = database.collection.insert_one(
            calldata.model_dump(by_alias=True, exclude=["id"])  # type: ignore
        )
        logger.info(f"{calldata.talkgroup_tag} - New document _ID: {inserted.inserted_id}")
        newcall: Call = Call(**database.collection.find_one({"_id": inserted.inserted_id}))
        #logger.info(newcall)
        #if not os.environ.get("TS_KEEPAUDIOFILES", None):
        #    os.remove(filepath)
    except Exception as e:
        logger.error(e)
        raise FileUploadException
    return newcall
