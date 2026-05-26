# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

人物信息管理系统 Pro — a Telegram bot + FastAPI backend that lets users manage personal contact info via natural language. OpenAI interprets free-form Chinese/English queries into structured CRUD operations on per-user JSON files.

## Running the System

Activate the venv first:
```bash
source venv/bin/activate
```

Both processes must run concurrently:

```bash
# Terminal 1: API backend
python api_service.py       # Listens on 127.0.0.1:8001

# Terminal 2: Telegram bot
python telegram_bot.py      # Long-polls Telegram
```

Install dependencies if needed (venv already set up):
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

The bot calls `http://localhost:8001/query` — change `API_URL` in `telegram_bot.py` if deploying remotely. Port 8000 is occupied by an unrelated Django project at `/root/bookmark/`.

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

**Error handling:** When OpenAI fails, `process_user_request` catches the exception and returns an error string. The API still returns HTTP 200 with that string in `answer` — there is no HTTP error propagation from the AI layer.

## Testing the Query Engine Directly

`query_engine.py` has a built-in test sequence (CRUD on a user `test_123`). Run it without the full stack:

```bash
python query_engine.py
```

This writes/reads `user_data/people_test_123.json` and exercises the full OpenAI round-trip.

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
- The AI model is `gpt-4.1-mini` with `response_format={"type": "json_object"}` (OpenAI JSON mode). Any replacement model must support JSON mode — the structured output contract is the core of the system.
- The system prompt in `query_engine.py` references "2026年" for age calculations — update annually.
- The load-modify-save pattern in `query_engine.py` is not concurrency-safe; simultaneous requests for the same `user_id` can race. Not an issue with the current single-process setup, but relevant if adding workers.
