# (Meeting Minutes)[https://meeting-minutes.kaizero.dev]

회의 녹음 파일을 업로드하면 자동으로 회의록을 생성하는 웹 앱

- **STT**: 로컬 Whisper 모델로 음성을 텍스트로 변환
- **LLM**: OpenRouter API를 통해 회의록 자동 작성
- **출력**: 요약, 주요 논의사항, 결정사항, 액션아이템

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI (Python) |
| STT | OpenAI Whisper (로컬) |
| LLM | OpenRouter API |

## 시작하기

### 사전 요구사항

- Python 3.10+
- Node.js 18+
- [OpenRouter API Key](https://openrouter.ai/keys)

### 설치

```bash
# 백엔드
cd backend
pip install -r requirements.txt
cp .env.sample .env
# .env 파일에서 OPENROUTER_API_KEY를 실제 키로 수정

# 프론트엔드
cd ../frontend
npm install
```

### 실행

```bash
# 백엔드 (포트 8000)
cd backend
uvicorn main:app --port 8000 --reload

# 프론트엔드 (포트 5173)
cd frontend
npm run dev
```

브라우저에서 http://localhost:5173 접속

### 테스트

```bash
cd backend
python3 -m pytest -v
```

## 사용법

1. 오디오 파일(mp3, wav) 업로드
2. LLM 모델 선택
3. "회의록 생성" 클릭
4. 좌측 STT 원문 / 우측 회의록 확인
5. 마크다운 다운로드

## 프로젝트 구조

```
meeting-minutes/
├── backend/
│   ├── main.py              # FastAPI 앱
│   ├── routers/
│   │   └── generate.py      # POST /api/generate
│   ├── services/
│   │   ├── stt.py           # Whisper STT
│   │   └── llm.py           # OpenRouter LLM
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # 메인 앱
│   │   └── components/
│   │       ├── FileUpload.jsx
│   │       ├── ResultView.jsx
│   │       ├── TranscriptPanel.jsx
│   │       └── MinutesPanel.jsx
│   └── vite.config.js
└── README.md
```
