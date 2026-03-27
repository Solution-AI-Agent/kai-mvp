import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.stt import transcribe_audio
from services.llm import generate_minutes

router = APIRouter()


def _build_markdown(minutes: dict, transcript: str) -> str:
    md = "# 회의록\n\n"
    md += f"## 요약\n\n{minutes['summary']}\n\n"
    md += "## 주요 논의사항\n\n"
    for item in minutes["discussions"]:
        md += f"- {item}\n"
    md += "\n## 결정사항\n\n"
    for item in minutes["decisions"]:
        md += f"- {item}\n"
    md += "\n## 액션아이템\n\n"
    for item in minutes["actionItems"]:
        md += f"- {item}\n"
    md += f"\n---\n\n## STT 원문\n\n{transcript}\n"
    return md


@router.post("/api/generate")
async def generate(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or ".wav")[1]
    if suffix.lower() not in (".mp3", ".wav"):
        raise HTTPException(status_code=400, detail="mp3 또는 wav 파일만 지원합니다.")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        transcript = transcribe_audio(tmp_path)
        minutes = await generate_minutes(transcript)
        markdown = _build_markdown(minutes, transcript)
    finally:
        os.unlink(tmp_path)

    return {
        "transcript": transcript,
        "summary": minutes["summary"],
        "discussions": minutes["discussions"],
        "decisions": minutes["decisions"],
        "actionItems": minutes["actionItems"],
        "markdown": markdown,
    }
