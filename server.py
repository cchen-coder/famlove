"""
FamSync WhatsApp Agent Server
Port 5051 — handles Twilio webhooks and serves FamSync data via REST API.

Setup:
  pip install -r requirements.txt
  cp .env.example .env && fill in values
  python server.py

Twilio webhook URL: https://<your-ngrok>.ngrok.io/webhook
"""

import os
import sys
from pathlib import Path

# allow imports from this directory
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from twilio.twiml.messaging_response import MessagingResponse
import uvicorn

from storage import Storage
from agent import FamSyncAgent

app = FastAPI(title="FamSync WhatsApp Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

storage = Storage()
agent = FamSyncAgent(storage)

# ── WhatsApp webhook (Twilio) ──────────────────────────────────────────────────

@app.post("/webhook")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(default=""),
    ProfileName: str = Form(default="")
):
    """Twilio sends POST form data here when a WhatsApp message arrives."""
    from_name = ProfileName or None  # Twilio includes sender's WhatsApp display name
    reply = agent.process_message(From, Body, from_name=from_name)

    resp = MessagingResponse()
    resp.message(reply)
    return HTMLResponse(content=str(resp), media_type="text/xml")


# ── REST API for FamSync frontend ─────────────────────────────────────────────

@app.get("/api/data")
async def get_data():
    """FamSync frontend polls this to get live data."""
    return JSONResponse(storage.load())


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "FamSync WhatsApp Agent"}


# ── Local test endpoint ───────────────────────────────────────────────────────

@app.post("/api/chat")
async def local_chat(request: Request):
    """Test the agent locally without WhatsApp. POST {phone, message, from_name}."""
    body = await request.json()
    phone = body.get("phone", "test-user")
    message = body.get("message", "")
    from_name = body.get("from_name")
    if not message:
        return JSONResponse({"error": "message required"}, status_code=400)
    reply = agent.process_message(phone, message, from_name=from_name)
    return JSONResponse({"reply": reply})


@app.post("/api/travel/suggest")
async def travel_suggest(request: Request):
    """Call Claude to get AI travel suggestions for a destination."""
    body = await request.json()
    destination = body.get("destination", "")
    trip_name = body.get("trip_name", "")
    dates = body.get("dates", "")
    if not destination:
        return JSONResponse({"error": "destination required"}, status_code=400)

    import anthropic as _anthropic
    import json as _json
    _client = _anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    prompt = (
        f"You are a Singapore-based family travel expert. Give practical suggestions for a family trip to {destination}"
        + (f" (trip: {trip_name}" + (f", dates: {dates}" if dates else "") + ")" if trip_name else "")
        + ".\n\nReturn a JSON object with exactly these four keys:\n"
        + '"things_to_do": list of 5-6 specific family-friendly activities/attractions\n'
        + '"food": list of 4-5 must-try local dishes or food spots\n'
        + '"packing_tips": list of 4-5 practical packing tips for this destination\n'
        + '"budget_tips": list of 4-5 money-saving tips in SGD for Singaporean families\n\n'
        + "Be specific and practical. Return ONLY valid JSON with no additional text."
    )
    message = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        result = _json.loads(raw)
    except Exception:
        result = {"things_to_do": [f"Visit {destination}"], "food": [], "packing_tips": [], "budget_tips": []}
    return JSONResponse(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5051))
    print(f"Famlove WhatsApp Agent starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
