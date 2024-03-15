from typing import List

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import RedirectResponse

from .controllers import *
from .models import *

app = FastAPI()


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.get(
    "/calls",
    response_model=List[Call],
    response_model_exclude_none=True,
    name="Get Lots of Calls",
)
def get_multiple_calls(skip: int = 0, limit: int = 10) -> list[Call]:

    if (limit >= 100) or (limit < 1):
        raise HTTPException(status_code=400, detail="Limit out of bounts 1-100")
    calllist: List[Call] = calls.get_calls(skip=skip, limit=limit)
    if not calllist:
        raise HTTPException(status_code=404, detail="No calls found!")

    return calllist


@app.get("/calls/{callid}", response_model=Call, response_model_exclude_none=True)
def get_single_call(callid: str) -> Call:
    call = calls.get_call(callid)
    if not call:
        raise HTTPException(status_code=404, detail="Call Not Found")
    return call


@app.post("/calls/upload")
def upload_call(calljsonfile: UploadFile, audiofile: UploadFile) -> Call:
    """Upload a call JSON and Call Audio files. Returns the Updated Call Object."""

    if not calljsonfile or not audiofile:
        raise HTTPException(
            status_code=400, detail="Must upload a CallJSON and Audio File"
        )

    calljsonfilename = calljsonfile.filename
    if not calljsonfilename:
        raise HTTPException(status_code=400)

    if audiofile.filename and not audiofile.filename.startswith(calljsonfilename[:-5]):
        raise HTTPException(
            status_code=400, detail="Call and Audio files must be for the same call"
        )

    ##Valid Upload, Process Call Here##
    try:
        call = handle_new_call(calljsonfile, audiofile)
    except FileUploadException as e:
        raise HTTPException(status_code=422)
    return call


@app.post("/calls/{callid}/transcript")
def add_transcription_to_call(callid: int, transcript: str):
    """Adds a transcript to an existing call identified by callid"""
    pass
