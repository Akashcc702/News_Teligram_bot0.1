import os
import requests
import time

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")

BASE_URL = "https://newsapi.org/v2/top-headlines"

CATEGORIES = [
    "technology",
    "sports",
    "business",
    "health",
    "entertainment",
    "science"
]


def fetch_news(category):
    params = {
        "apiKey": NEWS_API_KEY,
        "country": "in",
        "category": category,
        "pageSize": 5
    }

    for _ in range(3):  # retry logic
        try:
            res = requests.get(BASE_URL, params=params, timeout=10)
            if res.status_code == 200:
                return res.json().get("articles", [])
        except Exception:
            time.sleep(2)

    return []


def summarize_with_gemma(title, description):
    prompt = f"""
Summarize the news in 120 words.

Title: {title}
Description: {description}

Keep it simple, clean, and human-readable.
"""

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GEMMA_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "google/gemma-3-12b-it:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    for _ in range(3):
        try:
            res = requests.post(url, headers=headers, json=data, timeout=15)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            time.sleep(2)

    return description or "Summary unavailable."


def process_category(category):
    articles = fetch_news(category)
    processed = []

    for article in articles:
        title = article.get("title", "No Title")
        desc = article.get("description", "")

        summary = summarize_with_gemma(title, desc)

        processed.append({
            "headline": title,
            "summary": summary,
            "url": article.get("url", "")
        })

    return processed


def fetch_all_news():
    all_news = {}

    for cat in CATEGORIES:
        all_news[cat] = process_category(cat)

    return all_news
