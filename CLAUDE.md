# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: FamSync + WhatsApp Agent

**FamSync** is a single-file family management web app (`index.html`). The **WhatsApp Agent** (`whatsapp_agent/`) is a Python backend that lets family members update FamSync data by sending natural language messages via WhatsApp.

## Running the WhatsApp Agent

```bash
cd whatsapp_agent
cp .env.example .env        # fill in ANTHROPIC_API_KEY and Twilio credentials
pip install -r requirements.txt
python server.py             # starts on port 5051
```

Expose to the internet for Twilio webhook (dev):
```bash
ngrok http 5051
# set Twilio sandbox webhook to: https://<id>.ngrok.io/webhook
```

Test without WhatsApp:
```bash
curl -X POST http://localhost:5051/api/chat \
  -H "Content-Type: application/json" \
  -d '{"phone":"test","message":"Add milk to groceries","from_name":"Mom"}'
```

## Viewing FamSync

Open `index.html` directly in a browser. When the agent server is running on port 5051, FamSync auto-polls `http://localhost:5051/api/data` every 15 seconds and merges live data. A small dot in the topbar is green when connected, grey when offline.

## Architecture

### `index.html`
Single-file app — CSS → HTML markup → vanilla JS. Global state is `S` (tasks, events, groceries, expenses, habits, messages, goals, notifications). `renderPage()` re-renders based on `S.page`. Navigation calls `nav(pageId)`.

Live data sync: `syncFromAgent()` fetches from the agent API and merges into `S`, then calls `renderPage()`. Runs on load and every 15 seconds.

### `whatsapp_agent/`

| File | Role |
|------|------|
| `server.py` | FastAPI app — `/webhook` (Twilio POST), `/api/data` (GET), `/api/chat` (test POST) |
| `agent.py` | `FamSyncAgent` — per-phone conversation history, agentic loop with Claude |
| `tools.py` | Tool definitions (`TOOLS`) + `execute_tool()` dispatcher |
| `storage.py` | Thread-safe JSON read/write to `data.json` |
| `data.json` | Live FamSync data (auto-created on first run with defaults) |

### Data flow

```
WhatsApp user → Twilio → POST /webhook → FamSyncAgent.process_message()
  → Claude (tool_use loop) → execute_tool() → data.json
  → reply back to WhatsApp

FamSync frontend → GET /api/data (every 15s) → data.json → S state → renderPage()
```

### Tools available to the agent

`add_task`, `complete_task`, `add_event`, `add_grocery`, `check_grocery`, `add_expense`, `send_family_message`, `add_habit`, `log_habit`, `get_summary`, `update_goal`

### Twilio setup

1. Create Twilio account → Messaging → Try it out → WhatsApp sandbox
2. Set webhook URL to `https://<ngrok>.ngrok.io/webhook` (POST)
3. Each family member texts the join code to +1 415 523 8886

### Adding new FamSync data types

1. Add default data to `storage.py → _default_data()`
2. Add tool definition to `TOOLS` in `tools.py`
3. Add handler in `execute_tool()` in `tools.py`
4. Apply the new field in `_applyAgentData()` in `index.html`
