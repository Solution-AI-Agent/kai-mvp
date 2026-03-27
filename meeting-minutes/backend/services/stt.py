import os
import whisper

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    model = _get_model()
    result = model.transcribe(file_path, language="ko")
    return result["text"].strip()
