from ..models import *
from fastapi import UploadFile

class FileUploadException(Exception):
    pass

def handle_new_call(calldata: Call, file: UploadFile) -> Call:
    filepath = f"./uploads/{file.filename}"
    try:
        with open(filepath, "wxb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise FileUploadException
    calldata.id = file.size
    return calldata
    pass