import json
import os
from pathlib import Path
from threading import Lock

DATA_FILE = Path(__file__).parent / "data.json"
_lock = Lock()


class Storage:
    def load(self) -> dict:
        with _lock:
            if not DATA_FILE.exists():
                default = self._default_data()
                self._write(default)
                return default
            with open(DATA_FILE, "r") as f:
                return json.load(f)

    def save(self, data: dict) -> None:
        with _lock:
            self._write(data)

    def _write(self, data: dict) -> None:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def _default_data(self) -> dict:
        return {
            "tasks": [
                {"id": "t1", "title": "Pay electricity bill", "assignee": "Mom", "isChore": False, "done": False, "points": 0, "timeOfDay": "Any Time"},
                {"id": "t2", "title": "Clean room", "assignee": "Leo", "isChore": True, "done": False, "points": 50, "timeOfDay": "Morning"},
                {"id": "t3", "title": "Take out trash", "assignee": "Leo", "isChore": True, "done": True, "points": 30, "timeOfDay": "Evening"},
                {"id": "t4", "title": "Vacuum living room", "assignee": "Mia", "isChore": True, "done": False, "points": 40, "timeOfDay": "Morning"},
                {"id": "t5", "title": "Set dinner table", "assignee": "Mia", "isChore": True, "done": True, "points": 20, "timeOfDay": "Evening"}
            ],
            "events": [
                {"id": "e1", "title": "Soccer Practice", "date": "2026-04-22", "time": "3:00 PM", "assignee": "Leo", "type": "sport"},
                {"id": "e2", "title": "Dentist", "date": "2026-04-23", "time": "12:51 PM", "assignee": "Mom", "type": "appointment"},
                {"id": "e3", "title": "Leo's Piano", "date": "2026-04-24", "time": "4:00 PM", "assignee": "Leo", "type": "kids"},
                {"id": "e4", "title": "Mia's Checkup", "date": "2026-04-25", "time": "10:00 AM", "assignee": "Mia", "type": "kids"}
            ],
            "groceries": [
                {"id": "g1", "name": "Milk", "category": "Dairy", "checked": False, "fromMeal": False, "scheduledDay": "Monday"},
                {"id": "g2", "name": "Eggs", "category": "Dairy", "checked": False, "fromMeal": False, "scheduledDay": "Monday"},
                {"id": "g3", "name": "Pasta", "category": "Pantry", "checked": True, "fromMeal": True, "scheduledDay": "Tuesday"},
                {"id": "g4", "name": "Ground Beef", "category": "Meat", "checked": False, "fromMeal": True, "scheduledDay": "Tuesday"},
                {"id": "g5", "name": "Avocado", "category": "Produce", "checked": False, "fromMeal": True, "scheduledDay": "Wednesday"},
                {"id": "g6", "name": "Sourdough Bread", "category": "Bakery", "checked": False, "fromMeal": True, "scheduledDay": "Wednesday"}
            ],
            "expenses": [
                {"id": "x1", "date": "2026-04-22", "desc": "April rent", "category": "Housing", "paidBy": "Mom", "amount": 1000},
                {"id": "x2", "date": "2026-04-21", "desc": "Weekly groceries", "category": "Groceries", "paidBy": "Mom", "amount": 120.50},
                {"id": "x3", "date": "2026-04-20", "desc": "Internet bill", "category": "Utilities", "paidBy": "Dad", "amount": 60}
            ],
            "habits": [
                {"id": "h1", "name": "Morning walk", "streak": 5, "color": "#D85A30", "owner": "Mom", "days": [1, 1, 1, 1, 1, 0, 0], "addedBy": "parent"},
                {"id": "h2", "name": "Read 20 minutes", "streak": 3, "color": "#534AB7", "owner": "Leo", "days": [0, 1, 1, 1, 0, 0, 0], "addedBy": "parent"},
                {"id": "h3", "name": "Drink 8 glasses of water", "streak": 7, "color": "#0F6E56", "owner": "Mom", "days": [1, 1, 1, 1, 1, 1, 1], "addedBy": "parent"}
            ],
            "messages": [
                {"id": "msg1", "type": "announcement", "from": "Mom", "text": "Don't forget to take out the trash!", "time": "Apr 22, 12:51 PM"},
                {"id": "msg2", "from": "Leo", "text": "Can we have pizza tonight?", "time": "10:58 AM"},
                {"id": "msg3", "from": "Mom", "text": "Already planned Spaghetti Bolognese!", "time": "10:59 AM"}
            ],
            "goals": [
                {"id": "gl1", "title": "Family Vacation", "category": "Savings", "current": 500, "target": 2000, "color": "#D85A30"},
                {"id": "gl2", "title": "Emergency Fund", "category": "Savings", "current": 3200, "target": 5000, "color": "#0F6E56"}
            ],
            "notifications": [
                {"id": "n1", "title": "Dentist appointment tomorrow", "sub": "Wed Apr 23 • 12:51 PM", "color": "#D85A30", "unread": True},
                {"id": "n2", "title": "Pay electricity bill due today", "sub": "Assigned to Mom", "color": "#BA7517", "unread": True}
            ]
        }
