import io
import json
import wave
import struct
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _make_wav_bytes() -> bytes:
    """테스트용 1초 무음 wav 파일 바이트를 생성한다."""
    buf = io.BytesIO()
    with wave.open(buf, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        frames = struct.pack("<" + "h" * 16000, *([0] * 16000))
        f.writeframes(frames)
    buf.seek(0)
    return buf.read()


def test_generate_endpoint_success():
    """오디오 파일을 업로드하면 transcript와 회의록을 반환해야 한다."""
    mock_minutes = {
        "summary": "테스트 요약",
        "discussions": ["논의 1"],
        "decisions": ["결정 1"],
        "actionItems": ["액션 1"],
    }

    with patch("routers.generate.transcribe_audio", return_value="변환된 텍스트") as mock_stt, \
         patch("routers.generate.generate_minutes", new_callable=AsyncMock, return_value=mock_minutes) as mock_llm:

        wav_bytes = _make_wav_bytes()
        response = client.post(
            "/api/generate",
            files={"file": ("test.wav", wav_bytes, "audio/wav")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["transcript"] == "변환된 텍스트"
    assert data["summary"] == "테스트 요약"
    assert "markdown" in data


def test_generate_endpoint_no_file():
    """파일 없이 요청하면 422를 반환해야 한다."""
    response = client.post("/api/generate")
    assert response.status_code == 422
