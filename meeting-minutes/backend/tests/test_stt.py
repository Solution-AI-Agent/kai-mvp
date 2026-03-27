import os
import pytest
from services.stt import transcribe_audio


def test_transcribe_audio_returns_string(tmp_path):
    """실제 Whisper 모델로 무음 파일을 변환하면 빈 문자열 또는 텍스트를 반환해야 한다."""
    # 짧은 무음 wav 파일 생성
    import wave
    import struct

    audio_path = tmp_path / "silence.wav"
    with wave.open(str(audio_path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        # 1초 무음
        frames = struct.pack("<" + "h" * 16000, *([0] * 16000))
        f.writeframes(frames)

    result = transcribe_audio(str(audio_path))
    assert isinstance(result, str)


def test_transcribe_audio_invalid_file():
    """존재하지 않는 파일이면 FileNotFoundError를 발생시켜야 한다."""
    with pytest.raises(FileNotFoundError):
        transcribe_audio("/nonexistent/file.wav")
