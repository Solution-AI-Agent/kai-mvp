import json
import os
import httpx

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """당신은 회의록 작성 전문가입니다.
주어진 회의 텍스트를 분석하여 아래 JSON 형식으로 회의록을 작성하세요.
반드시 유효한 JSON만 출력하세요. 다른 텍스트는 포함하지 마세요.

{
  "summary": "회의 전체 내용을 2-3문장으로 요약",
  "discussions": ["주요 논의사항 1", "주요 논의사항 2", ...],
  "decisions": ["결정사항 1", "결정사항 2", ...],
  "actionItems": ["액션아이템 1", "액션아이템 2", ...]
}"""


async def generate_minutes(transcript: str) -> dict:
    if not transcript.strip():
        raise ValueError("Transcript is empty")

    api_key = os.environ.get("OPENROUTER_API_KEY", "")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": transcript},
                ],
            },
            timeout=60.0,
        )

    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)
