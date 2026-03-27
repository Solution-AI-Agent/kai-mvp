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


async def generate_minutes(transcript: str, model: str = "openai/gpt-4o-mini") -> dict:
    if not transcript.strip():
        raise ValueError("Transcript is empty")

    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY 환경변수가 설정되지 않았습니다.")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": transcript},
                ],
            },
            timeout=120.0,
        )

    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter API 오류 (HTTP {response.status_code}): {response.text}")

    data = response.json()
    if "error" in data:
        raise RuntimeError(f"OpenRouter API 오류: {data['error'].get('message', data['error'])}")

    content = data["choices"][0]["message"]["content"]

    # LLM이 ```json ... ``` 으로 감싸는 경우 처리
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        lines = lines[1:]  # ```json 제거
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # 닫는 ``` 제거
        content = "\n".join(lines).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise RuntimeError(f"LLM 응답을 JSON으로 파싱할 수 없습니다: {content[:200]}")
