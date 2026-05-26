# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

人物信息管理系统 Pro — a Telegram bot + FastAPI backend that lets users manage personal contact info via natural language. OpenAI interprets free-form Chinese/English queries into structured CRUD operations on per-user JSON files.

## Running the System

Both processes must run concurrently:

```bash
# Terminal 1: API backend
python api_service.py       # Listens on 0.0.0.0:8000

# Terminal 2: Telegram bot
python telegram_bot.py      # Long-polls Telegram
```

Install dependencies (no requirements.txt — use venv):
```bash
pip install fastapi uvicorn openai requests python-telegram-bot python-dotenv
```

## Environment Setup

Copy `.env.example` to `.env` and fill in real values:
```
OPENAI_API_KEY=<key>
BASE_URL=<openai-compatible endpoint, e.g. https://api.gptsapi.net/v1>
TELEGRAM_BOT_TOKEN=<telegram bot token>
```

The bot calls `http://localhost:8000/query` — change `API_URL` in `telegram_bot.py` if deploying remotely.

## Architecture

```
Telegram User
     │  natural language message
     ▼
telegram_bot.py          — captures user_id + message, POSTs to API
     │  POST /query {user_id, query}
     ▼
api_service.py           — FastAPI, validates request, calls query engine
     │
     ▼
query_engine.py          — loads user JSON, sends (data + query) to OpenAI,
     │                     receives {new_data, reply}, saves updated JSON
     ▼
user_data/people_{user_id}.json   — one file per Telegram user ID
```

**The AI loop in `query_engine.py`:** The system prompt instructs GPT to act as a JSON data manager. Every request sends the full current dataset + user query; GPT returns `{"new_data": [...], "reply": "..."}`. `new_data` replaces the file entirely; `reply` is sent back to the user. Temperature is 0.3 for determinism.

## Data Model

Per-user file: `user_data/people_{user_id}.json` — a JSON array of objects. Fields are dynamic; the AI creates/renames them as needed. Common fields seen in practice:

```json
{
  "name": "陈依凡",
  "age": 25,
  "gender": "女",
  "shoe_size": 37.0,
  "gifts": ["香水", "乐高"],
  "other": "喜欢猫，对花生过敏"
}
```

Only `name` is required for creation. The AI auto-converts units (e.g. "38码" → 38).

## Key Design Constraints

- **No traditional database** — all persistence is flat JSON files in `user_data/`.
- **Multi-user isolation** is purely file-based on Telegram `user_id`.
- `manage_people.py` is a legacy standalone CLI; it is **not part of the Pro system** and operates on `people.json`, not `user_data/`.
- The AI model is `gpt-4.1-mini`. Changing models affects cost and latency; the structured JSON output format must be preserved.
- The system prompt in `query_engine.py` references "2026年" for age calculations — update annually.
