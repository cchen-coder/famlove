import json
import os
from datetime import datetime
from typing import Optional
import pytz
import anthropic
from storage import Storage
from tools import TOOLS, execute_tool

SGT = pytz.timezone("Asia/Singapore")

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are Famlove Assistant, an AI helper for a Singapore family management app.

Family members: Mom (parent), Dad (parent), Leo (age 10, kid), Mia (age 8, kid).
Location: Singapore (SGT, UTC+8). Currency: SGD ($).

Today is {today} (Singapore time). Users message you via WhatsApp to update Famlove — their shared family app that tracks tasks, calendar events, groceries, expenses, habits, goals, family messages, and holiday trips/travel plans.

How to handle messages:
- Parse natural language and use the right tool(s) to update FamSync data
- For dates like "tomorrow", "Friday", "next week" — convert to YYYY-MM-DD based on today's date in Singapore
- For multiple items (e.g. "add milk, eggs, butter to groceries") — use add_grocery with all items in one call
- Understand Singlish and common SG terms (e.g. "kopitiam", "NTUC" = grocery store, "MC" = medical cert/sick leave, "makan" = eat/meal)
- Amounts are in SGD by default
- Always confirm what you did in a short, friendly WhatsApp-style reply (keep under 200 chars when possible)
- If unclear who the message is from, ask once. Use the "from_name" hint if provided
- Never make up data or assume things that weren't said"""


class FamSyncAgent:
    def __init__(self, storage: Storage):
        self.storage = storage
        # per-phone conversation history: phone -> [{"role": ..., "content": ...}]
        self._conversations: dict[str, list] = {}

    def process_message(self, phone: str, text: str, from_name: Optional[str] = None) -> str:
        history = self._conversations.setdefault(phone, [])

        # Build user turn
        user_content = text
        if from_name:
            user_content = f"[{from_name}]: {text}"
        history.append({"role": "user", "content": user_content})

        # Keep last 20 turns to avoid token blow-up
        if len(history) > 20:
            history[:] = history[-20:]

        system = SYSTEM_PROMPT.format(
            today=datetime.now(SGT).strftime("%Y-%m-%d (%A)")
        )

        messages = list(history)

        # Agentic loop
        for _ in range(5):  # max 5 tool-call rounds
            response = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1024,
                system=system,
                tools=TOOLS,
                messages=messages
            )

            if response.stop_reason == "tool_use":
                assistant_turn = {"role": "assistant", "content": response.content}
                messages.append(assistant_turn)

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = execute_tool(block.name, block.input, self.storage)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result)
                        })

                messages.append({"role": "user", "content": tool_results})

            elif response.stop_reason == "end_turn":
                reply = "".join(
                    block.text for block in response.content if hasattr(block, "text")
                )
                history.append({"role": "assistant", "content": reply})
                return reply

            else:
                break

        return "Sorry, I couldn't process that. Please try again."
