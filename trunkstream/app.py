from typing import List

from fastapi import FastAPI, HTTPException, UploadFile
from sqlmodel import create_engine, SQLModel, Session, select

from .models import *
from .controllers import *
import json




sqlite_file_name = "database.db"
sqlite_file_name = ":memory:"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    pass
    #SQLModel.metadata.create_all(engine)


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/calls/", response_model=List[Call], response_model_exclude_none=True)
def get_calls(skip: int = 0, limit: int = 10) -> list[Call]:

    if (limit >= 100) or (limit < 1):
        raise HTTPException(status_code=400, detail="Limit out of bounts 1-100")

    return [mock_call(x) for x in range(skip, limit)]

@app.get("/calls/{callid}", response_model=Call, response_model_exclude_none=True)
def get_single_call(callid: int) -> Call:
    return mock_call(callid)

@app.post("/calls/upload/")
def upload_call(files: List[UploadFile]) -> Call:

    if len(files) != 2:
        raise HTTPException(status_code=400)

    calljsonfilelist = [f for f in files if f.content_type and f.content_type == 'application/json']
    calljsonfile = calljsonfilelist[0] if calljsonfilelist else None

    audiofilelist = [
        f for f in files if f.content_type and f.content_type == 'audio/x-m4a'
    ]
    audiofile = audiofilelist[0] if audiofilelist else None

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
        call = handle_new_call(Call(**json.load(calljsonfile.file)), audiofile)
    except FileUploadException as e:
        raise HTTPException(status_code=422)
    return call
