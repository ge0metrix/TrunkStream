from ..models import *
from fastapi import UploadFile
import json
from ..dbmodels import database
from icad_tone_detection import tone_detect

class FileUploadException(Exception):
    pass

def handle_new_call(calljsonfile: UploadFile, audiofile: UploadFile) -> Call:
    calldata = Call(**json.load(calljsonfile.file))
    filepath = f"./uploads/{audiofile.filename}"
    try:
        #with open(filepath, "wxb") as f:
        #    f.write(audiofile.file.read())
        calldata.filepath = audiofile.filename
        t = tone_detect(audiofile.file)
        print(t.hi_low_result, t.long_result, t.two_tone_result)
        detected = DetectedTones(hi_low=t.hi_low_result, quick_call=t.two_tone_result, long=t.long_result)
        calldata.tones = [detected]
        inserted = database.collection.insert_one(calldata.model_dump(by_alias=True, exclude=["id"]))
        print(inserted.inserted_id)
        newcall:Call = database.collection.find_one({"_id": inserted.inserted_id})
        print(newcall)
    except Exception as e:
        print(e)
        raise FileUploadException
    return newcall
