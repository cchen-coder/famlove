from datetime import datetime
from typing import Any, Dict
import pytz
from storage import Storage

SGT = pytz.timezone("Asia/Singapore")


def now_sgt() -> datetime:
    return datetime.now(SGT)

TOOLS = [
    {
        "name": "add_task",
        "description": "Add a new task or chore to FamSync",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "assignee": {"type": "string", "description": "Mom, Dad, Leo, Mia, or All"},
                "isChore": {"type": "boolean", "description": "True if this is a kids chore"},
                "points": {"type": "integer", "description": "Reward points for completing (0 for adult tasks)"},
                "timeOfDay": {"type": "string", "description": "Morning, Afternoon, Evening, or Any Time"}
            },
            "required": ["title", "assignee"]
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as done or undone",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title (partial match)"},
                "done": {"type": "boolean", "description": "True to mark done, False to unmark"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "add_event",
        "description": "Add a calendar event or appointment",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "time": {"type": "string", "description": "e.g. '3:00 PM' or 'All Day'"},
                "assignee": {"type": "string", "description": "Mom, Dad, Leo, Mia, or All"},
                "type": {"type": "string", "description": "appointment, sport, kids, birthday, or other"}
            },
            "required": ["title", "date", "assignee"]
        }
    },
    {
        "name": "add_grocery",
        "description": "Add one or more items to the grocery list",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string", "description": "Dairy, Produce, Meat, Pantry, Bakery, Frozen, Beverages, or Other"},
                            "scheduledDay": {"type": "string"}
                        },
                        "required": ["name"]
                    }
                }
            },
            "required": ["items"]
        }
    },
    {
        "name": "check_grocery",
        "description": "Mark grocery item(s) as bought or uncheck them",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Item name (partial match)"},
                "checked": {"type": "boolean", "description": "True = bought, False = still needed"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "add_expense",
        "description": "Log a family expense",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "category": {"type": "string", "description": "Housing, Groceries, Utilities, Medical, Transport, Entertainment, or Other"},
                "paid_by": {"type": "string", "description": "Mom or Dad"},
                "amount": {"type": "number"},
                "date": {"type": "string", "description": "YYYY-MM-DD, defaults to today"}
            },
            "required": ["description", "amount", "paid_by"]
        }
    },
    {
        "name": "send_family_message",
        "description": "Post a message to the family hub chat",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_name": {"type": "string", "description": "Mom, Dad, Leo, or Mia"},
                "text": {"type": "string"}
            },
            "required": ["from_name", "text"]
        }
    },
    {
        "name": "add_habit",
        "description": "Add a new habit to track for a family member",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "owner": {"type": "string", "description": "Mom, Dad, Leo, or Mia"},
                "color": {"type": "string", "description": "Hex color, optional"}
            },
            "required": ["name", "owner"]
        }
    },
    {
        "name": "log_habit",
        "description": "Mark a habit as done today",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Habit name (partial match)"},
                "done": {"type": "boolean", "description": "True if completed today"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_summary",
        "description": "Get today's summary: events, pending tasks, and grocery count",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "update_goal",
        "description": "Update progress on a savings or personal goal",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Goal title (partial match)"},
                "current": {"type": "number", "description": "New current amount saved/achieved"}
            },
            "required": ["title", "current"]
        }
    },
    {
        "name": "create_trip",
        "description": "Create a new holiday plan / trip in Famlove",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Name of the trip e.g. Bali Family Holiday"},
                "destination": {"type": "string", "description": "Destination e.g. Bali, Indonesia"},
                "start_date": {"type": "string", "description": "Start date e.g. 10 Aug 2026"},
                "end_date": {"type": "string", "description": "End date e.g. 20 Aug 2026"},
                "budget": {"type": "number", "description": "Budget in SGD"}
            },
            "required": ["trip_name", "destination"]
        }
    },
    {
        "name": "add_itinerary_item",
        "description": "Add an activity to a trip itinerary",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "title": {"type": "string", "description": "Activity or place name"},
                "day": {"type": "string", "description": "Date e.g. 11 Aug 2026"},
                "time": {"type": "string", "description": "Time e.g. 10:00 AM"},
                "type": {"type": "string", "description": "activity, attraction, restaurant, flight, hotel, or car"},
                "notes": {"type": "string", "description": "Any notes"}
            },
            "required": ["trip_name", "title", "day"]
        }
    },
    {
        "name": "add_bucket_item",
        "description": "Add a wish to a trip's bucket list",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "title": {"type": "string", "description": "Bucket list wish"},
                "category": {"type": "string", "description": "Adventure, Food, Culture, Kids, Nature, or Other"}
            },
            "required": ["trip_name", "title"]
        }
    },
    {
        "name": "add_packing_item",
        "description": "Add an item to a trip's packing list",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "item": {"type": "string", "description": "Item to pack"},
                "category": {"type": "string", "description": "Documents, Health, Clothing, Electronics, Kids, or Other"},
                "who": {"type": "string", "description": "Who needs it: All, Mom, Dad, Leo, or Mia"}
            },
            "required": ["trip_name", "item"]
        }
    },
    {
        "name": "get_trip_summary",
        "description": "Get a summary of a holiday plan's status",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match), or omit for first trip"}
            },
            "required": []
        }
    },
    {
        "name": "update_trip",
        "description": "Update details of an existing holiday plan (name, destination, dates, budget)",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Current trip name (partial match)"},
                "new_name": {"type": "string", "description": "New trip name"},
                "destination": {"type": "string", "description": "New destination"},
                "start_date": {"type": "string", "description": "New start date e.g. 10 Aug 2026"},
                "end_date": {"type": "string", "description": "New end date e.g. 20 Aug 2026"},
                "budget": {"type": "number", "description": "New total budget in SGD"}
            },
            "required": ["trip_name"]
        }
    },
    {
        "name": "delete_trip",
        "description": "Delete an entire holiday plan",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"}
            },
            "required": ["trip_name"]
        }
    },
    {
        "name": "update_itinerary_item",
        "description": "Edit an activity in a trip's itinerary",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "title": {"type": "string", "description": "Current activity title (partial match)"},
                "new_title": {"type": "string", "description": "New title"},
                "day": {"type": "string", "description": "New date e.g. 12 Aug 2026"},
                "time": {"type": "string", "description": "New time e.g. 2:00 PM"},
                "type": {"type": "string", "description": "activity, attraction, restaurant, flight, hotel, or car"},
                "notes": {"type": "string", "description": "New notes"}
            },
            "required": ["trip_name", "title"]
        }
    },
    {
        "name": "delete_itinerary_item",
        "description": "Remove an activity from a trip's itinerary",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "title": {"type": "string", "description": "Activity title (partial match)"}
            },
            "required": ["trip_name", "title"]
        }
    },
    {
        "name": "toggle_itinerary_done",
        "description": "Mark a trip activity as done or not done",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "title": {"type": "string", "description": "Activity title (partial match)"},
                "done": {"type": "boolean", "description": "True = completed, False = not done yet"}
            },
            "required": ["trip_name", "title"]
        }
    },
    {
        "name": "update_bucket_item",
        "description": "Edit a wish on a trip's bucket list",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "title": {"type": "string", "description": "Current wish title (partial match)"},
                "new_title": {"type": "string", "description": "New wish title"},
                "category": {"type": "string", "description": "Adventure, Food, Culture, Kids, Nature, or Other"}
            },
            "required": ["trip_name", "title"]
        }
    },
    {
        "name": "delete_bucket_item",
        "description": "Remove a wish from a trip's bucket list",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "title": {"type": "string", "description": "Wish title (partial match)"}
            },
            "required": ["trip_name", "title"]
        }
    },
    {
        "name": "toggle_bucket_done",
        "description": "Mark a bucket list wish as done or undone",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "title": {"type": "string", "description": "Wish title (partial match)"},
                "done": {"type": "boolean", "description": "True = done, False = not done"}
            },
            "required": ["trip_name", "title"]
        }
    },
    {
        "name": "update_packing_item",
        "description": "Edit an item on a trip's packing list",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "item": {"type": "string", "description": "Current item name (partial match)"},
                "new_item": {"type": "string", "description": "New item name"},
                "category": {"type": "string", "description": "Documents, Health, Clothing, Electronics, Kids, or Other"},
                "who": {"type": "string", "description": "All, Mom, Dad, Leo, or Mia"}
            },
            "required": ["trip_name", "item"]
        }
    },
    {
        "name": "delete_packing_item",
        "description": "Remove an item from a trip's packing list",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "item": {"type": "string", "description": "Item name (partial match)"}
            },
            "required": ["trip_name", "item"]
        }
    },
    {
        "name": "toggle_packed",
        "description": "Mark a packing item as packed or still needed",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "item": {"type": "string", "description": "Item name (partial match)"},
                "packed": {"type": "boolean", "description": "True = packed, False = still needed"}
            },
            "required": ["trip_name", "item"]
        }
    },
    {
        "name": "add_travel_expense",
        "description": "Log an expense for a specific trip",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "description": {"type": "string", "description": "What the expense was for"},
                "amount": {"type": "number", "description": "Amount in SGD"},
                "paid_by": {"type": "string", "description": "Who paid: Mom, Dad, or Family"},
                "category": {"type": "string", "description": "Food, Transport, Accommodation, Activities, Shopping, or Other"}
            },
            "required": ["trip_name", "description", "amount"]
        }
    },
    {
        "name": "delete_travel_expense",
        "description": "Remove an expense from a trip",
        "input_schema": {
            "type": "object",
            "properties": {
                "trip_name": {"type": "string", "description": "Trip name (partial match)"},
                "description": {"type": "string", "description": "Expense description (partial match)"}
            },
            "required": ["trip_name", "description"]
        }
    }
]


def execute_tool(name: str, inputs: Dict[str, Any], storage: Storage) -> Dict:
    data = storage.load()
    today = now_sgt().strftime("%Y-%m-%d")

    if name == "add_task":
        new_id = f"t{len(data['tasks']) + 1}"
        task = {
            "id": new_id,
            "title": inputs["title"],
            "assignee": inputs.get("assignee", "All"),
            "isChore": inputs.get("isChore", False),
            "done": False,
            "points": inputs.get("points", 0),
            "timeOfDay": inputs.get("timeOfDay", "Any Time")
        }
        data["tasks"].append(task)
        storage.save(data)
        return {"success": True, "message": f"Added task: {task['title']} → {task['assignee']}"}

    elif name == "complete_task":
        q = inputs["title"].lower()
        done = inputs.get("done", True)
        for t in data["tasks"]:
            if q in t["title"].lower():
                t["done"] = done
                storage.save(data)
                return {"success": True, "message": f"'{t['title']}' marked {'done' if done else 'undone'}"}
        return {"success": False, "message": "Task not found"}

    elif name == "add_event":
        new_id = f"e{len(data['events']) + 1}"
        event = {
            "id": new_id,
            "title": inputs["title"],
            "date": inputs["date"],
            "time": inputs.get("time", "All Day"),
            "assignee": inputs.get("assignee", "All"),
            "type": inputs.get("type", "other")
        }
        data["events"].append(event)
        storage.save(data)
        return {"success": True, "message": f"Added: {event['title']} on {event['date']} at {event['time']}"}

    elif name == "add_grocery":
        added = []
        for item in inputs.get("items", []):
            new_id = f"g{len(data['groceries']) + 1}"
            entry = {
                "id": new_id,
                "name": item["name"],
                "category": item.get("category", "Other"),
                "checked": False,
                "fromMeal": False,
                "scheduledDay": item.get("scheduledDay", "")
            }
            data["groceries"].append(entry)
            added.append(item["name"])
        storage.save(data)
        return {"success": True, "message": f"Added to groceries: {', '.join(added)}"}

    elif name == "check_grocery":
        q = inputs["name"].lower()
        checked = inputs.get("checked", True)
        for g in data["groceries"]:
            if q in g["name"].lower():
                g["checked"] = checked
                storage.save(data)
                return {"success": True, "message": f"'{g['name']}' marked as {'bought' if checked else 'still needed'}"}
        return {"success": False, "message": "Grocery item not found"}

    elif name == "add_expense":
        new_id = f"x{len(data['expenses']) + 1}"
        expense = {
            "id": new_id,
            "date": inputs.get("date", today),
            "desc": inputs["description"],
            "category": inputs.get("category", "Other"),
            "paidBy": inputs.get("paid_by", "Mom"),
            "amount": float(inputs["amount"])
        }
        data["expenses"].append(expense)
        storage.save(data)
        return {"success": True, "message": f"Logged ${expense['amount']:.2f} for {expense['desc']}"}

    elif name == "send_family_message":
        new_id = f"msg{len(data['messages']) + 1}"
        msg = {
            "id": new_id,
            "from": inputs["from_name"],
            "text": inputs["text"],
            "time": now_sgt().strftime("%b %d, %I:%M %p")
        }
        data["messages"].append(msg)
        storage.save(data)
        return {"success": True, "message": "Message posted to family hub"}

    elif name == "add_habit":
        new_id = f"h{len(data['habits']) + 1}"
        habit = {
            "id": new_id,
            "name": inputs["name"],
            "streak": 0,
            "color": inputs.get("color", "#D85A30"),
            "owner": inputs.get("owner", "All"),
            "days": [0, 0, 0, 0, 0, 0, 0],
            "addedBy": "whatsapp"
        }
        data["habits"].append(habit)
        storage.save(data)
        return {"success": True, "message": f"Added habit '{habit['name']}' for {habit['owner']}"}

    elif name == "log_habit":
        q = inputs["name"].lower()
        done = inputs.get("done", True)
        day_idx = now_sgt().weekday()
        for h in data["habits"]:
            if q in h["name"].lower():
                h["days"][day_idx] = 1 if done else 0
                if done:
                    h["streak"] = h.get("streak", 0) + 1
                storage.save(data)
                return {"success": True, "message": f"Habit '{h['name']}' logged as {'done' if done else 'skipped'} today"}
        return {"success": False, "message": "Habit not found"}

    elif name == "get_summary":
        today_events = [e for e in data.get("events", []) if e.get("date") == today]
        pending = [t for t in data.get("tasks", []) if not t.get("done")]
        groceries_left = [g for g in data.get("groceries", []) if not g.get("checked")]
        return {
            "success": True,
            "today": today,
            "events_today": [f"{e['title']} at {e.get('time','?')}" for e in today_events],
            "pending_tasks": len(pending),
            "groceries_needed": len(groceries_left)
        }

    elif name == "update_goal":
        q = inputs["title"].lower()
        for g in data.get("goals", []):
            if q in g["title"].lower():
                g["current"] = float(inputs["current"])
                storage.save(data)
                pct = int(g["current"] / g["target"] * 100)
                return {"success": True, "message": f"'{g['title']}' updated to ${g['current']:.0f} ({pct}% of ${g['target']:.0f})"}
        return {"success": False, "message": "Goal not found"}

    elif name == "create_trip":
        import random as _random
        import time as _time
        emojis = ['🌴', '🗼', '🏝', '🗺', '🌏', '🏔', '🌆', '🎡', '🏖', '🌿']
        colors = ['#0F6E56', '#E24B4A', '#185FA5', '#D4537E', '#BA7517', '#534AB7', '#D85A30']
        start = inputs.get('start_date', '')
        end = inputs.get('end_date', '')
        dates = f"{start} – {end}" if start and end else start or end or 'TBD'
        trip = {
            "id": f"t{int(_time.time())}",
            "tripName": inputs["trip_name"],
            "destination": inputs["destination"],
            "dates": dates,
            "emoji": _random.choice(emojis),
            "color": _random.choice(colors),
            "budget": float(inputs.get("budget", 0)),
            "spent": 0,
            "itinerary": [], "bookings": [], "bucketList": [], "packing": [], "expenses": [],
            "emergency": {"hospital": "", "ambulance": "", "police": "", "embassy": "", "transport": "", "currency": "", "language": ""}
        }
        if "trips" not in data:
            data["trips"] = []
        data["trips"].append(trip)
        storage.save(data)
        return {"success": True, "message": f"Created trip '{trip['tripName']}' to {trip['destination']} ({dates})"}

    elif name == "add_itinerary_item":
        q = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        import time as _time2
        item = {
            "id": f"i{int(_time2.time())}",
            "day": inputs["day"],
            "time": inputs.get("time", ""),
            "title": inputs["title"],
            "type": inputs.get("type", "activity"),
            "notes": inputs.get("notes", ""),
            "assignee": "All",
            "done": False
        }
        trip["itinerary"].append(item)
        storage.save(data)
        return {"success": True, "message": f"Added '{item['title']}' to {trip['tripName']} on {item['day']}"}

    elif name == "add_bucket_item":
        q = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        import time as _time3
        item = {
            "id": f"bl{int(_time3.time())}",
            "title": inputs["title"],
            "category": inputs.get("category", "Other"),
            "addedBy": "WhatsApp",
            "liked": [],
            "done": False
        }
        trip["bucketList"].append(item)
        storage.save(data)
        return {"success": True, "message": f"Added '{item['title']}' to bucket list for {trip['tripName']}"}

    elif name == "add_packing_item":
        q = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        import time as _time4
        item = {
            "id": f"pk{int(_time4.time())}",
            "item": inputs["item"],
            "category": inputs.get("category", "Other"),
            "packed": False,
            "who": inputs.get("who", "All")
        }
        trip["packing"].append(item)
        storage.save(data)
        return {"success": True, "message": f"Added '{item['item']}' to packing list for {trip['tripName']}"}

    elif name == "get_trip_summary":
        q = inputs.get("trip_name", "").lower()
        trips = data.get("trips", [])
        if q:
            trip = next((t for t in trips if q in t["tripName"].lower()), None)
        else:
            trip = trips[0] if trips else None
        if not trip:
            names = [t["tripName"] for t in trips]
            return {"success": False, "message": "No trips found." if not names else f"Trip not found. Available: {', '.join(names)}"}
        done = sum(1 for i in trip["itinerary"] if i.get("done"))
        packed = sum(1 for p in trip["packing"] if p.get("packed"))
        return {
            "success": True,
            "trip": trip["tripName"],
            "destination": trip["destination"],
            "dates": trip["dates"],
            "budget_sgd": trip["budget"],
            "activities": f"{done}/{len(trip['itinerary'])} done",
            "bucket_list": f"{len(trip['bucketList'])} wishes",
            "packing": f"{packed}/{len(trip['packing'])} packed"
        }

    elif name == "update_trip":
        q = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        if inputs.get("new_name"):
            trip["tripName"] = inputs["new_name"]
        if inputs.get("destination"):
            trip["destination"] = inputs["destination"]
        if inputs.get("start_date") or inputs.get("end_date"):
            s = inputs.get("start_date", "")
            e = inputs.get("end_date", "")
            if s and e:
                trip["dates"] = f"{s} – {e}"
            elif s:
                trip["dates"] = s
            elif e:
                trip["dates"] = e
        if inputs.get("budget") is not None:
            trip["budget"] = float(inputs["budget"])
        storage.save(data)
        return {"success": True, "message": f"Updated trip '{trip['tripName']}' — dest: {trip['destination']}, dates: {trip['dates']}, budget: ${trip['budget']:.0f}"}

    elif name == "delete_trip":
        q = inputs["trip_name"].lower()
        before = len(data.get("trips", []))
        data["trips"] = [t for t in data.get("trips", []) if q not in t["tripName"].lower()]
        if len(data["trips"]) == before:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        storage.save(data)
        return {"success": True, "message": f"Deleted trip matching '{inputs['trip_name']}'"}

    elif name == "update_itinerary_item":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_item = inputs["title"].lower()
        item = next((i for i in trip["itinerary"] if q_item in i["title"].lower()), None)
        if not item:
            return {"success": False, "message": f"Activity '{inputs['title']}' not found in {trip['tripName']}"}
        if inputs.get("new_title"):
            item["title"] = inputs["new_title"]
        if inputs.get("day"):
            item["day"] = inputs["day"]
        if inputs.get("time"):
            item["time"] = inputs["time"]
        if inputs.get("type"):
            item["type"] = inputs["type"]
        if inputs.get("notes") is not None:
            item["notes"] = inputs["notes"]
        storage.save(data)
        return {"success": True, "message": f"Updated activity '{item['title']}' in {trip['tripName']}"}

    elif name == "delete_itinerary_item":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_item = inputs["title"].lower()
        before = len(trip["itinerary"])
        trip["itinerary"] = [i for i in trip["itinerary"] if q_item not in i["title"].lower()]
        if len(trip["itinerary"]) == before:
            return {"success": False, "message": f"Activity '{inputs['title']}' not found"}
        storage.save(data)
        return {"success": True, "message": f"Removed activity '{inputs['title']}' from {trip['tripName']}"}

    elif name == "toggle_itinerary_done":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_item = inputs["title"].lower()
        item = next((i for i in trip["itinerary"] if q_item in i["title"].lower()), None)
        if not item:
            return {"success": False, "message": f"Activity '{inputs['title']}' not found"}
        item["done"] = inputs.get("done", not item.get("done", False))
        storage.save(data)
        status = "done ✅" if item["done"] else "not done"
        return {"success": True, "message": f"'{item['title']}' marked {status}"}

    elif name == "update_bucket_item":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_item = inputs["title"].lower()
        item = next((b for b in trip["bucketList"] if q_item in b["title"].lower()), None)
        if not item:
            return {"success": False, "message": f"Wish '{inputs['title']}' not found"}
        if inputs.get("new_title"):
            item["title"] = inputs["new_title"]
        if inputs.get("category"):
            item["category"] = inputs["category"]
        storage.save(data)
        return {"success": True, "message": f"Updated wish '{item['title']}' in {trip['tripName']}"}

    elif name == "delete_bucket_item":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_item = inputs["title"].lower()
        before = len(trip["bucketList"])
        trip["bucketList"] = [b for b in trip["bucketList"] if q_item not in b["title"].lower()]
        if len(trip["bucketList"]) == before:
            return {"success": False, "message": f"Wish '{inputs['title']}' not found"}
        storage.save(data)
        return {"success": True, "message": f"Removed '{inputs['title']}' from bucket list"}

    elif name == "toggle_bucket_done":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_item = inputs["title"].lower()
        item = next((b for b in trip["bucketList"] if q_item in b["title"].lower()), None)
        if not item:
            return {"success": False, "message": f"Wish '{inputs['title']}' not found"}
        item["done"] = inputs.get("done", not item.get("done", False))
        storage.save(data)
        status = "done ✅" if item["done"] else "not done"
        return {"success": True, "message": f"'{item['title']}' marked {status}"}

    elif name == "update_packing_item":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_item = inputs["item"].lower()
        item = next((p for p in trip["packing"] if q_item in p["item"].lower()), None)
        if not item:
            return {"success": False, "message": f"Packing item '{inputs['item']}' not found"}
        if inputs.get("new_item"):
            item["item"] = inputs["new_item"]
        if inputs.get("category"):
            item["category"] = inputs["category"]
        if inputs.get("who"):
            item["who"] = inputs["who"]
        storage.save(data)
        return {"success": True, "message": f"Updated packing item '{item['item']}' (for {item['who']})"}

    elif name == "delete_packing_item":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_item = inputs["item"].lower()
        before = len(trip["packing"])
        trip["packing"] = [p for p in trip["packing"] if q_item not in p["item"].lower()]
        if len(trip["packing"]) == before:
            return {"success": False, "message": f"Packing item '{inputs['item']}' not found"}
        storage.save(data)
        return {"success": True, "message": f"Removed '{inputs['item']}' from packing list"}

    elif name == "toggle_packed":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_item = inputs["item"].lower()
        item = next((p for p in trip["packing"] if q_item in p["item"].lower()), None)
        if not item:
            return {"success": False, "message": f"Packing item '{inputs['item']}' not found"}
        item["packed"] = inputs.get("packed", not item.get("packed", False))
        storage.save(data)
        status = "packed ✅" if item["packed"] else "unpacked"
        return {"success": True, "message": f"'{item['item']}' marked {status}"}

    elif name == "add_travel_expense":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        import time as _time5
        expense = {
            "id": f"te{int(_time5.time())}",
            "desc": inputs["description"],
            "amount": float(inputs["amount"]),
            "paidBy": inputs.get("paid_by", "Family"),
            "date": today,
            "category": inputs.get("category", "Other"),
            "split": "Family"
        }
        trip["expenses"].append(expense)
        total = sum(e["amount"] for e in trip["expenses"])
        remaining = trip["budget"] - total
        storage.save(data)
        return {"success": True, "message": f"Logged ${expense['amount']:.2f} for {expense['desc']}. Trip spent: ${total:.0f} / ${trip['budget']:.0f} (${remaining:.0f} left)"}

    elif name == "delete_travel_expense":
        q_trip = inputs["trip_name"].lower()
        trip = next((t for t in data.get("trips", []) if q_trip in t["tripName"].lower()), None)
        if not trip:
            return {"success": False, "message": f"Trip '{inputs['trip_name']}' not found"}
        q_exp = inputs["description"].lower()
        before = len(trip["expenses"])
        trip["expenses"] = [e for e in trip["expenses"] if q_exp not in e["desc"].lower()]
        if len(trip["expenses"]) == before:
            return {"success": False, "message": f"Expense '{inputs['description']}' not found"}
        storage.save(data)
        return {"success": True, "message": f"Removed expense matching '{inputs['description']}' from {trip['tripName']}"}

    return {"success": False, "message": f"Unknown tool: {name}"}
