import json
import os
from datetime import datetime

DATA_FILE = "news_data.json"


def save_news(data: dict):
    payload = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "data": data
    }
    with open(DATA_FILE, "w") as f:
        json.dump(payload, f)


def load_news():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        payload = json.load(f)

    return payload


def is_today_data():
    payload = load_news()
    if not payload:
        return False

    today = datetime.utcnow().strftime("%Y-%m-%d")
    return payload.get("date") == today


def get_news_by_category(category: str):
    payload = load_news()
    if not payload:
        return []

    return payload.get("data", {}).get(category, [])
