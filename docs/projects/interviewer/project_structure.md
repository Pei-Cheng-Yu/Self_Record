#  Project Directory Structure

A modular, monorepo-style structure to separate the **React frontend** from the **Python/LangGraph backend**.

```text
Interviewer-App/
├── backend/                         # Python/FastAPI/LangGraph Logic
│   ├── app/                         # Main FastAPI application code
│   │   ├── api/                     # API routers (endpoints)
│   │   │   ├── __init__.py
│   │   │   └── interview_router.py  # Endpoints: /start, /chat, /report
│   │   ├── core/                    # LangGraph "Brain"
│   │   │   ├── __init__.py
│   │   │   ├── agent.py             # Graph orchestration (the "sewing" logic)
│   │   │   ├── state.py             # Shared InterviewState definition
│   │   │   └── agents/              # Modular Agent Logic
│   │   │       ├── __init__.py
│   │   │       ├── onboarding/
│   │   │       │   ├── node.py
│   │   │       │   └── tools.py     # RAG ingestion tools
│   │   │       ├── interviewer/
│   │   │       │   ├── node.py
│   │   │       │   └── tools.py     # ElevenLabs TTS tool
│   │   │       ├── scoring/
│   │   │       │   └── node.py      # Logic for scoring & next_action
│   │   │       ├── preparation/
│   │   │       │   └── node.py      # Next Question Generator (parallel)
│   │   │       ├── case/
│   │   │       │   └── node.py      # Case Agent: work sample + rubric + scoring
│   │   │       └── review/
│   │   │           └── node.py      # Report generation
│   │   ├── rag/                     # RAG Components
│   │   │   ├── __init__.py
│   │   │   └── vector_store.py      # Vertex AI / local vector DB setup
│   │   └── main.py                  # App entry point
│   ├── .env                         # API keys (Gemini, ElevenLabs, Google Cloud)
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/                        # React Application
    ├── src/
    │   ├── components/              # UI components (VoiceRecorder, ChatBubble)
    │   ├── pages/                   # Views (Onboarding, Session, Report)
    │   ├── services/                # API client (axios/fetch)
    │   └── App.js
    └── package.json
```
