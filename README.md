# HCPFiller - Full-Stack Production Boilerplate

## Overview
Production-ready scaffold with **FastAPI + LangGraph** backend and **React + Redux Toolkit + Tailwind CSS** frontend. The AI sidebar communicates with the backend, receives structured JSON from LangGraph tool calls, and auto-populates form fields via Redux dispatch.

## Directory Tree

```
HCPFiller/
├── Backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  ← FastAPI entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── health.py
│   │   │           └── ai.py        ← AI chat/fill endpoint
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            ← Pydantic Settings
│   │   │   ├── database.py          ← SQLAlchemy async engine
│   │   │   └── exceptions.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── ai.py                ← AI request/response schemas
│   │   │   └── form.py              ← FormData schema
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── ai_service.py        ← Orchestrates LangGraph
│   │   └── agent/
│   │       ├── __init__.py
│   │       ├── graph.py             ← LangGraph StateGraph
│   │       ├── state.py             ← AgentState TypedDict
│   │       └── tools/
│   │           ├── __init__.py
│   │           └── form_filler.py   ← LangGraph tool: fill_form
│   ├── .env.template
│   ├── requirements.txt
│   └── README.md
│
└── Frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── store/
    │   │   ├── store.js             ← Redux store configuration
    │   │   └── slices/
    │   │       ├── formSlice.js     ← Form fields state
    │   │       └── aiSlice.js       ← AI chat state
    │   ├── api/
    │   │   └── aiApi.js             ← Axios calls to FastAPI
    │   ├── components/
    │   │   ├── MainForm.jsx         ← Multi-field form
    │   │   ├── AIButton.jsx         ← Floating button
    │   │   └── AISidebar.jsx        ← AI chat sidebar
    │   └── hooks/
    │       └── useAI.js             ← Custom hook for AI interactions
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    └── .env.template
```


## 🚀 Getting Started

### 1. Backend Setup
1. `cd Backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.template` to `.env` and add your `GROQ_API_KEY`.
6. Run the server: `python -m app.main` (or `uvicorn app.main:app --reload`)

### 2. Frontend Setup
1. `cd Frontend`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`
4. Open `http://localhost:5173`

## 🧠 AI Integration
The AI Assistant in the sidebar uses **LangGraph** to process user messages. When it detects form-related information, it triggers the `fill_form` tool, which returns structured JSON. The frontend Redux store catches this and automatically populates the corresponding form fields.

## 🛠️ Tech Stack
- **Backend**: FastAPI, LangGraph, Pydantic v2, SQLModel, SQLAlchemy.
- **Frontend**: React, Redux Toolkit, Vite, Tailwind CSS.
- **AI**: Groq (Llama 3 70B).
