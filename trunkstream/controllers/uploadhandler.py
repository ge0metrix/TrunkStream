import json

from fastapi import UploadFile
from icad_tone_detection import tone_detect

from ..dbmodels import database
from ..models import *
import os
import logging

logger = logging.getLogger("uvicorn.error")

class FileUploadException(Exception):
    pass


def handle_new_call(calljsonfile: UploadFile, audiofile: UploadFile) -> Call:
    calldata = Call(**json.load(calljsonfile.file))
    filepath = f"./uploads/{audiofile.filename}"
    try:
        if os.environ.get("TS_SAVELOCAL", None):
            with open(filepath, "wb") as f:
                f.write(audiofile.file.read())
        calldata.filepath = filepath
        audiofile.file.seek(0)
        try: 
            if calldata.call_length > 3:
                t = tone_detect(audiofile.file)
                detected = DetectedTones(
                    hi_low=t.hi_low_result, quick_call=t.two_tone_result, long=t.long_result
                )
                calldata.tones = detected
            else:
                logger.warn(f"Call Too Short: {calldata.call_length}")
                
        except ValueError as e:
            print(e)
        inserted = database.collection.insert_one(
            calldata.model_dump(by_alias=True, exclude=["id"])  # type: ignore
        )
        logger.info(f"New document _ID: {inserted.inserted_id}")
        newcall: Call = database.collection.find_one({"_id": inserted.inserted_id})  # type: ignore
    except Exception as e:
        print(e)
        raise FileUploadException
    return newcall
