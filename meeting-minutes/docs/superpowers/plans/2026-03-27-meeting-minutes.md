# 회의록 생성 앱 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 오디오 파일을 업로드하면 로컬 Whisper로 STT 변환 후 OpenRouter LLM으로 회의록을 자동 생성하는 웹 앱

**Architecture:** FastAPI 백엔드가 오디오 파일을 받아 Whisper STT → OpenRouter LLM 파이프라인을 처리하고, React(Vite) 프론트엔드가 업로드 UI와 결과(STT 원문 좌 / 회의록 우)를 표시한다. DB/인증 없이 일회성 처리.

**Tech Stack:** React, Vite, Tailwind CSS, FastAPI, openai-whisper, OpenRouter API, pytest, vitest

---

## 파일 구조

```
meeting-minutes/
├── backend/
│   ├── main.py                  # FastAPI 앱, CORS, 라우터 마운트
│   ├── routers/
│   │   └── generate.py          # POST /api/generate 엔드포인트
│   ├── services/
│   │   ├── stt.py               # Whisper STT 서비스
│   │   └── llm.py               # OpenRouter LLM 서비스
│   ├── requirements.txt         # Python 의존성
│   └── tests/
│       ├── test_stt.py          # STT 서비스 테스트
│       ├── test_llm.py          # LLM 서비스 테스트
│       └── test_generate.py     # API 엔드포인트 테스트
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── src/
│   │   ├── main.jsx             # React 엔트리
│   │   ├── index.css            # Tailwind + 글로벌 스타일
│   │   ├── App.jsx              # 메인 앱 컴포넌트
│   │   ├── components/
│   │   │   ├── FileUpload.jsx   # 파일 업로드 컴포넌트
│   │   │   ├── ResultView.jsx   # 결과 2컬럼 레이아웃
│   │   │   ├── TranscriptPanel.jsx  # STT 원문 패널
│   │   │   └── MinutesPanel.jsx     # 회의록 패널
│   │   └── __tests__/
│   │       ├── FileUpload.test.jsx
│   │       └── ResultView.test.jsx
│   └── .env
└── CLAUDE.md
```

---

### Task 1: 백엔드 프로젝트 셋업

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`

- [ ] **Step 1: requirements.txt 생성**

```txt
fastapi==0.115.0
uvicorn==0.30.0
python-multipart==0.0.9
openai-whisper==20240930
httpx==0.27.0
pytest==8.3.0
pytest-asyncio==0.24.0
```

- [ ] **Step 2: FastAPI 앱 생성**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Meeting Minutes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 3: 서버 실행 확인**

Run: `cd backend && pip install -r requirements.txt && uvicorn main:app --port 8000 &`
Run: `curl http://localhost:8000/health`
Expected: `{"status":"ok"}`

- [ ] **Step 4: 커밋**

```bash
git add backend/requirements.txt backend/main.py
git commit -m "feat: 백엔드 프로젝트 셋업 (FastAPI)"
```

---

### Task 2: STT 서비스 구현

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/stt.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_stt.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/test_stt.py
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
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && python -m pytest tests/test_stt.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'services.stt'`

- [ ] **Step 3: STT 서비스 구현**

```python
# backend/services/__init__.py
```

```python
# backend/services/stt.py
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
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/test_stt.py -v`
Expected: 2 passed

- [ ] **Step 5: 커밋**

```bash
git add backend/services/ backend/tests/
git commit -m "feat: Whisper STT 서비스 구현"
```

---

### Task 3: LLM 서비스 구현

**Files:**
- Create: `backend/services/llm.py`
- Create: `backend/tests/test_llm.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/test_llm.py
import json
import pytest
from unittest.mock import patch, AsyncMock
from services.llm import generate_minutes


@pytest.mark.asyncio
async def test_generate_minutes_returns_structured_result():
    """LLM 응답을 파싱하여 구조화된 회의록을 반환해야 한다."""
    mock_llm_response = json.dumps({
        "summary": "테스트 회의 요약",
        "discussions": ["논의사항 1", "논의사항 2"],
        "decisions": ["결정사항 1"],
        "actionItems": ["액션아이템 1"]
    })

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": mock_llm_response}}]
    }

    with patch("services.llm.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await generate_minutes("회의 내용 텍스트")

    assert result["summary"] == "테스트 회의 요약"
    assert len(result["discussions"]) == 2
    assert len(result["decisions"]) == 1
    assert len(result["actionItems"]) == 1


@pytest.mark.asyncio
async def test_generate_minutes_empty_transcript():
    """빈 텍스트가 입력되면 ValueError를 발생시켜야 한다."""
    with pytest.raises(ValueError):
        await generate_minutes("")
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && python -m pytest tests/test_llm.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'services.llm'`

- [ ] **Step 3: LLM 서비스 구현**

```python
# backend/services/llm.py
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
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/test_llm.py -v`
Expected: 2 passed

- [ ] **Step 5: 커밋**

```bash
git add backend/services/llm.py backend/tests/test_llm.py
git commit -m "feat: OpenRouter LLM 서비스 구현"
```

---

### Task 4: API 엔드포인트 구현

**Files:**
- Create: `backend/routers/__init__.py`
- Create: `backend/routers/generate.py`
- Create: `backend/tests/test_generate.py`
- Modify: `backend/main.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/test_generate.py
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
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && python -m pytest tests/test_generate.py -v`
Expected: FAIL — router not found

- [ ] **Step 3: 엔드포인트 구현**

```python
# backend/routers/__init__.py
```

```python
# backend/routers/generate.py
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
```

- [ ] **Step 4: main.py에 라우터 등록**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.generate import router as generate_router

app = FastAPI(title="Meeting Minutes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/test_generate.py -v`
Expected: 2 passed

- [ ] **Step 6: 전체 백엔드 테스트 실행**

Run: `cd backend && python -m pytest -v`
Expected: 6 passed

- [ ] **Step 7: 커밋**

```bash
git add backend/routers/ backend/tests/test_generate.py backend/main.py
git commit -m "feat: POST /api/generate 엔드포인트 구현"
```

---

### Task 5: 프론트엔드 프로젝트 셋업

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/index.css`
- Create: `frontend/src/App.jsx`
- Create: `frontend/.env`

- [ ] **Step 1: Vite React 프로젝트 생성**

Run: `cd meeting-minutes && npm create vite@latest frontend -- --template react`

- [ ] **Step 2: 의존성 설치**

Run: `cd frontend && npm install && npm install -D tailwindcss @tailwindcss/vite`

- [ ] **Step 3: Tailwind 설정**

```js
// frontend/vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
```

```css
/* frontend/src/index.css */
@import "tailwindcss";

@theme {
  --color-emerald-400: #34d399;
  --color-emerald-500: #10b981;
  --color-emerald-600: #059669;
  --color-dark-800: #1e1e2e;
  --color-dark-900: #11111b;
  --color-dark-700: #313244;
}
```

- [ ] **Step 4: .env 파일 생성**

```
# frontend/.env
VITE_API_URL=http://localhost:8000
```

- [ ] **Step 5: App.jsx 기본 구조 작성**

```jsx
// frontend/src/App.jsx
function App() {
  return (
    <div className="min-h-screen bg-dark-900 text-gray-100">
      <header className="border-b border-dark-700 px-6 py-4">
        <h1 className="text-2xl font-bold text-emerald-400">
          KAI 회의록
        </h1>
      </header>
      <main className="p-6">
        <p className="text-gray-400">회의록 생성 앱</p>
      </main>
    </div>
  );
}

export default App;
```

- [ ] **Step 6: 개발 서버 실행 확인**

Run: `cd frontend && npm run dev`
Expected: 브라우저에서 `http://localhost:5173` 접속 시 다크 배경에 "KAI 회의록" 타이틀 표시

- [ ] **Step 7: 커밋**

```bash
git add frontend/
git commit -m "feat: 프론트엔드 프로젝트 셋업 (React + Vite + Tailwind)"
```

---

### Task 6: 파일 업로드 컴포넌트

**Files:**
- Create: `frontend/src/components/FileUpload.jsx`

- [ ] **Step 1: FileUpload 컴포넌트 구현**

```jsx
// frontend/src/components/FileUpload.jsx
import { useCallback } from "react";

export default function FileUpload({ onFileSelect, file, isLoading }) {
  const handleChange = useCallback(
    (e) => {
      const selected = e.target.files?.[0];
      if (selected) onFileSelect(selected);
    },
    [onFileSelect]
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      const dropped = e.dataTransfer.files?.[0];
      if (dropped) onFileSelect(dropped);
    },
    [onFileSelect]
  );

  return (
    <div className="flex items-center gap-4">
      <label
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="flex-1 flex items-center justify-center border-2 border-dashed border-dark-700 rounded-lg p-6 cursor-pointer hover:border-emerald-500 transition-colors"
      >
        <input
          type="file"
          accept=".mp3,.wav"
          onChange={handleChange}
          className="hidden"
          disabled={isLoading}
        />
        <span className="text-gray-400">
          {file ? file.name : "오디오 파일을 드래그하거나 클릭하여 선택 (mp3, wav)"}
        </span>
      </label>
    </div>
  );
}
```

- [ ] **Step 2: 커밋**

```bash
git add frontend/src/components/FileUpload.jsx
git commit -m "feat: 파일 업로드 컴포넌트 구현"
```

---

### Task 7: 결과 표시 컴포넌트

**Files:**
- Create: `frontend/src/components/TranscriptPanel.jsx`
- Create: `frontend/src/components/MinutesPanel.jsx`
- Create: `frontend/src/components/ResultView.jsx`

- [ ] **Step 1: TranscriptPanel 구현**

```jsx
// frontend/src/components/TranscriptPanel.jsx
export default function TranscriptPanel({ transcript }) {
  return (
    <div className="bg-dark-800 rounded-lg p-5 h-full overflow-y-auto">
      <h2 className="text-lg font-semibold text-emerald-400 mb-3">
        STT 원문
      </h2>
      <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">
        {transcript}
      </p>
    </div>
  );
}
```

- [ ] **Step 2: MinutesPanel 구현**

```jsx
// frontend/src/components/MinutesPanel.jsx
export default function MinutesPanel({ summary, discussions, decisions, actionItems }) {
  return (
    <div className="bg-dark-800 rounded-lg p-5 h-full overflow-y-auto space-y-5">
      <section>
        <h2 className="text-lg font-semibold text-emerald-400 mb-2">요약</h2>
        <p className="text-gray-300">{summary}</p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-emerald-400 mb-2">주요 논의사항</h2>
        <ul className="list-disc list-inside text-gray-300 space-y-1">
          {discussions.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-emerald-400 mb-2">결정사항</h2>
        <ul className="list-disc list-inside text-gray-300 space-y-1">
          {decisions.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-emerald-400 mb-2">액션아이템</h2>
        <ul className="list-disc list-inside text-gray-300 space-y-1">
          {actionItems.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
```

- [ ] **Step 3: ResultView 구현**

```jsx
// frontend/src/components/ResultView.jsx
import TranscriptPanel from "./TranscriptPanel";
import MinutesPanel from "./MinutesPanel";

export default function ResultView({ result }) {
  return (
    <div className="grid grid-cols-2 gap-4 h-[60vh]">
      <TranscriptPanel transcript={result.transcript} />
      <MinutesPanel
        summary={result.summary}
        discussions={result.discussions}
        decisions={result.decisions}
        actionItems={result.actionItems}
      />
    </div>
  );
}
```

- [ ] **Step 4: 커밋**

```bash
git add frontend/src/components/
git commit -m "feat: 결과 표시 컴포넌트 구현 (TranscriptPanel, MinutesPanel, ResultView)"
```

---

### Task 8: App 통합 및 API 연동

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: App.jsx에 전체 흐름 통합**

```jsx
// frontend/src/App.jsx
import { useState } from "react";
import FileUpload from "./components/FileUpload";
import ResultView from "./components/ResultView";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!file) return;

    setIsLoading(true);
    setError("");
    setResult(null);
    setStatus("STT 변환 중...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("회의록 생성 중...");
      const response = await fetch("/api/generate", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "서버 오류가 발생했습니다.");
      }

      const data = await response.json();
      setResult(data);
      setStatus("");
    } catch (err) {
      setError(err.message);
      setStatus("");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result?.markdown) return;
    const blob = new Blob([result.markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "회의록.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-dark-900 text-gray-100">
      <header className="border-b border-dark-700 px-6 py-4">
        <h1 className="text-2xl font-bold text-emerald-400">KAI 회의록</h1>
      </header>

      <main className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <FileUpload onFileSelect={setFile} file={file} isLoading={isLoading} />
          </div>
          <button
            onClick={handleGenerate}
            disabled={!file || isLoading}
            className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-dark-700 disabled:text-gray-500 rounded-lg font-semibold transition-colors"
          >
            {isLoading ? status : "회의록 생성"}
          </button>
        </div>

        {error && (
          <div className="bg-red-900/30 border border-red-700 text-red-300 rounded-lg p-4">
            {error}
          </div>
        )}

        {result && (
          <>
            <ResultView result={result} />
            <div className="flex justify-center">
              <button
                onClick={handleDownload}
                className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 rounded-lg font-semibold transition-colors"
              >
                마크다운 다운로드
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
```

- [ ] **Step 2: 개발 서버에서 UI 확인**

Run: `cd frontend && npm run dev`
Expected: 파일 업로드 영역, 회의록 생성 버튼이 다크+에메랄드 테마로 표시

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/App.jsx
git commit -m "feat: App 통합 - 파일 업로드, API 연동, 결과 표시, 다운로드"
```

---

### Task 9: E2E 통합 테스트

**Files:**
- Modify: `backend/tests/test_generate.py`

- [ ] **Step 1: 통합 테스트 보강**

기존 `test_generate.py`에 마크다운 응답 검증 추가:

```python
# backend/tests/test_generate.py 에 추가
def test_generate_endpoint_markdown_contains_sections():
    """응답의 markdown에 모든 섹션이 포함되어야 한다."""
    mock_minutes = {
        "summary": "테스트 요약",
        "discussions": ["논의 1"],
        "decisions": ["결정 1"],
        "actionItems": ["액션 1"],
    }

    with patch("routers.generate.transcribe_audio", return_value="변환된 텍스트"), \
         patch("routers.generate.generate_minutes", new_callable=AsyncMock, return_value=mock_minutes):

        wav_bytes = _make_wav_bytes()
        response = client.post(
            "/api/generate",
            files={"file": ("test.wav", wav_bytes, "audio/wav")},
        )

    md = response.json()["markdown"]
    assert "## 요약" in md
    assert "## 주요 논의사항" in md
    assert "## 결정사항" in md
    assert "## 액션아이템" in md
    assert "## STT 원문" in md


def test_generate_endpoint_rejects_invalid_format():
    """mp3/wav가 아닌 파일은 400 에러를 반환해야 한다."""
    response = client.post(
        "/api/generate",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
```

- [ ] **Step 2: 전체 테스트 실행**

Run: `cd backend && python -m pytest -v`
Expected: 8 passed

- [ ] **Step 3: 커밋**

```bash
git add backend/tests/test_generate.py
git commit -m "test: 통합 테스트 보강 - 마크다운 섹션 검증, 파일 형식 검증"
```
