from typing import List
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import RedirectResponse

from .controllers import *
from .models import *
from .worker import transcribe_call_task

import logging

logger = logging.getLogger(__name__)

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


@app.post("/calls/upload", response_model=Call)
def upload_call(calljsonfile: UploadFile, audiofile: UploadFile, background_tasks: BackgroundTasks) -> Call:
    """Upload a call JSON and Call Audio files. Returns the Updated Call Object."""
    logger.debug(calljsonfile.filename)
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
        logging.info(call.id, call.talkgroup_tag)
        x = transcribe_call_task.delay(call.id, call.filepath)
        logging.warn(x)
    except FileUploadException as e:
        raise HTTPException(status_code=422)
    return call
