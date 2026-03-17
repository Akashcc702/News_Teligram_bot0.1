import json
import os
from datetime import datetime

FILE = "news.json"

def save_news(data):
    payload = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "data": data
    }
    with open(FILE, "w") as f:
        json.dump(payload, f)

def load_news():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def is_today_data():
    data = load_news()
    if not data:
        return False
    return data.get("date") == datetime.utcnow().strftime("%Y-%m-%d")

def get_news_by_category(cat):
    data = load_news()
    return data.get("data", {}).get(cat, [])
