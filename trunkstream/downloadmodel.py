
from faster_whisper import WhisperModel, download_model
modeltype = 'large-v3'
model_cache_dir = f"/tmp/whispermodels/{modeltype}"
model_dir = download_model(
    modeltype,
    output_dir=model_cache_dir,
)