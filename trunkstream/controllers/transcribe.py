import glob
import logging
import os
from typing import BinaryIO
import warnings
from datetime import datetime, timedelta
from io import FileIO
from pprint import pprint
from time import time

from faster_whisper import WhisperModel, download_model
from ..models import *

logger = logging.getLogger(__name__)


def timed(func):
    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        logger.info(f"Function {func.__name__!r} executed in {(t2-t1):.4f}s")
        return result

    return wrap_func


config_data = {
    "log_level": 1,
    "audio_upload": {
        "allowed_extensions": [".wav", ".m4a", ".mp3"],
        "max_audio_length": 300,
        "max_file_size": 3,
    },
    "whisper": {
        "device": "cpu",
        "cpu_threads": 4,
        "compute_type": "float32",
        "model": "small.en",
        "language": "en",
        "beam_size": 5,
        "best_of": 1,
        "vad_filter": True,
        "vad_parameters": {
            "threshold": 0.5,
            "min_speech_duration_ms": 250,
            "max_speech_duration_s": 3600,
            "min_silence_duration_ms": 2000,
            "window_size_samples": 1024,
            "speech_pad_ms": 400,
        },
    },
}


def is_model_outdated(directory, days=7):
    """Check if the model files in the directory are older than 'days' days."""
    now = datetime.now()
    threshold = now - timedelta(days=days)

    if not os.path.exists(directory):
        # Directory does not exist, so model is considered outdated
        return True

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if file_mod_time < threshold:
            # At least one file is older than the threshold, so model is outdated
            return True

    # All files are within the 'days' threshold
    return False

@timed
def transcribe_call(callid: str, callaudio: str | FileIO | BinaryIO)->Transcript:
    if not callaudio:
        raise Exception("no call file for transcript")

    warnings.simplefilter("ignore")
    model_cache_dir = "./whispermodels/"
    model_dir = model_cache_dir
    if is_model_outdated(model_cache_dir):
        model_dir = download_model(
            config_data.get("model", "medium.en"), output_dir=model_cache_dir
        )

    if config_data.get("whisper", {}).get("device", None) in ["cpu", "cuda"]:
        model = WhisperModel(
            model_dir,
            device=config_data.get("whisper", {}).get("device", "cpu"),
            cpu_threads=config_data.get("whisper", {}).get("cpu_threads", 4),
            compute_type=config_data.get("whisper", {}).get("compute_type", "float32"),
        )
    else:
        raise Exception("No Whisper Config")
    logger.info(f"transcribing call: {callid}") # type: ignore
    segments, _ = model.transcribe(
        audio=callaudio,
        word_timestamps=False,
        best_of=5,
    )

    transcript: str = ""
    segmentlist = []
    for segment in segments:
        wordlist = []
        if segment.words:
            for word in segment.words:
                wordlist.append(Word(**word._asdict()))
        seg = Segment(
            id=segment.id,
            seek=segment.seek,
            start=segment.start,
            end=segment.end,
            text=segment.text,
            tokens=segment.tokens,
            temperature=segment.temperature,
            avg_logprob=segment.avg_logprob,
            compression_ratio=segment.compression_ratio,
            no_speech_prob=segment.no_speech_prob,
            words=wordlist,
        )
        segmentlist.append(seg)
        transcript += segment.text + "\n"

    transcriptdata: Transcript = Transcript(
        id=callid, segments=segmentlist, transcript=transcript
    )

    return transcriptdata


if __name__ == "__main__":
    x = 0
    path = "./examples/"
    for file in glob.glob(path + "*.m4a"):
        x += 1
        print(file)
        with open(file, "rb") as f:
            transcribe_call(f"{x}", f)
