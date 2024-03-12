from ..models import *
from fastapi import UploadFile
import json

class FileUploadException(Exception):
    pass

def handle_new_call(calljsonfile: UploadFile, audiofile: UploadFile) -> Call:
    calldata = Call(**json.load(calljsonfile.file))
    filepath = f"./uploads/{audiofile.filename}"
    try:
        with open(filepath, "wxb") as f:
            f.write(audiofile.file.read())
    except Exception as e:
        raise FileUploadException
    calldata.id = audiofile.size
    return calldata
