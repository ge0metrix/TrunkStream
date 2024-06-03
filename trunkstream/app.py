from typing import List
from io import BytesIO

from fastapi import FastAPI, HTTPException, Request, UploadFile, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .controllers import *
from .models import *
from .worker import transcribe_call_task, detect_tones_task

import logging

logger = logging.getLogger(__name__)

app = FastAPI()



BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

@app.get("/")
async def root(request: Request):
    calls = get_calls(limit=99)
    return TEMPLATES.TemplateResponse(
    "calllist.html",
    {"request": request, "calls":calls},
    )
@app.get("/system/{shortname}/")
async def short(request: Request, shortname:str):
    calls = get_calls(limit=1000, shortname=shortname)
    return TEMPLATES.TemplateResponse(
    "calllist.html",
    {"request": request, "calls":calls},
    )


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

@app.get("/calls/tones/")
def get_tone_calls() -> list[Call]:
    calls = get_calls_with_tones()
    return calls

@app.get("/calls/{callid}/transcript")
def get_call_transcript(callid: str, transcript:Transcript) -> Transcript:
    return calls.get_call(callid).transcript


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
        x = transcribe_call_task.delay(callid = call.id, filepath = call.filepath)
        logging.warn(f"transcribe id: {x}")
        if call.call_length > 2:
            x = detect_tones_task.delay(callid = call.id, filepath = call.filepath)
            logger.warn(f"tone detect id: {x}")
        else:
            logger.warn(f"Call Too Short: {call.call_length}")
    except FileUploadException as e:
        raise HTTPException(status_code=422)
    return call
