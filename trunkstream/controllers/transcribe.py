import glob
import logging
import os
import warnings
from datetime import datetime, timedelta
from io import FileIO
from typing import BinaryIO

from faster_whisper import WhisperModel, download_model

from ..models import *

logger = logging.getLogger(__name__)

config_data = {
    "whisper": {
        "device": "cpu",
        "cpu_threads": 4,
        "compute_type": "float32",
        "model": "large-v3",
        "language": "en",
        "beam_size": 5,
        "best_of": 5,
        "initial_prompt": "Westford Control",
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


def transcribe_call(callaudio: str | FileIO | BinaryIO) -> Transcript:
    if not callaudio:
        raise Exception("no call file for transcript")

    warnings.simplefilter("ignore")

    whisperconf = config_data.get("whisper", {})
    modeltype = whisperconf.get('model', 'medium.en')
    logger.info(f"Using model type: {modeltype}")
    model_cache_dir = f"/tmp/whispermodels/{modeltype}"
    model_dir = model_cache_dir
    if is_model_outdated(model_cache_dir):
        logger.info(f"Downloading Model {modeltype}")
        model_dir = download_model(
            modeltype,
            output_dir=model_cache_dir,
        )

    if whisperconf.get("device", None) in ["cpu", "cuda"]:
        model = WhisperModel(
            model_dir,
            device=whisperconf.get("device", "cpu"),
            cpu_threads=whisperconf.get("cpu_threads", 4),
            compute_type=whisperconf.get("compute_type", "float32"),
        )
    else:
        raise Exception("No Whisper Config")

    segments, _ = model.transcribe(
        audio=callaudio,
        word_timestamps=whisperconf.get("word_timestamps", False),
        best_of=whisperconf.get("best_of", 5),
        language=whisperconf.get("language", "en"),
        beam_size=whisperconf.get("beam_size", 5),
        temperature=0,
        initial_prompt=whisperconf.get("initial_prompt", ""),
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
    logger.info(transcript.replace("\n"," - "))
    transcriptdata: Transcript = Transcript(
        id="", segments=segmentlist, transcript=transcript
    )

    return transcriptdata


if __name__ == "__main__":
    x = 0
    path = "./examples/"
    for file in glob.glob(path + "*.m4a"):
        x += 1
        print(file)
        with open(file, "rb") as f:
            transcribe_call(f)
