#!/usr/bin/env python3
"""
News Telegram Bot - Render Ready (Free 24/7 Deployment)
Categories: Tech, Sports, Business, Entertainment, Science, Health
Auto-updates every 4 hours | /start | /refresh
"""
import os
import asyncio
import json
import sqlite3
from datetime import datetime, date
from threading import Thread
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "your-news-api-key-here")  # Free: newsapi.org

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("news.db", check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news 
                 (id INTEGER PRIMARY KEY, category TEXT, headline TEXT, url TEXT, 
                  date TEXT, fetched_date TEXT)''')
    conn.commit()
    conn.close()

def save_news(data):
    conn = sqlite3.connect("news.db", check_same_thread=False)
    c = conn.cursor()
    today = date.today().isoformat()
    for category, articles in data.items():
        for article in articles[:10]:  # Top 10 per category
            c.execute("INSERT OR REPLACE INTO news (category, headline, url, date, fetched_date) VALUES (?, ?, ?, ?, ?)",
                     (category, article['title'], article['url'], article['publishedAt'], today))
    conn.commit()
    conn.close()

def get_news_by_category(category):
    conn = sqlite3.connect("news.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT headline, url FROM news WHERE category=? ORDER BY date DESC LIMIT 5", (category,))
    news = [{"headline": row[0], "url": row[1]} for row in c.fetchall()]
    conn.close()
    return news

def is_today_data():
    conn = sqlite3.connect("news.db", check_same_thread=False)
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("SELECT COUNT(*) FROM news WHERE fetched_date=?", (today,))
    count = c.fetchone()[0]
    conn.close()
    return count > 10  # At least 10 articles today

# ================= NEWS FETCHER =================
async def fetch_all_news():
    """Fetch news from NewsAPI - Free tier works fine"""
    categories = {
        "technology": "technology",
        "sports": "sports", 
        "business": "business",
        "entertainment": "entertainment",
        "science": "science",
        "health": "health"
    }
    
    news_data = {}
    url = "https://newsapi.org/v2/top-headlines"
    
    for cat in categories.values():
        try:
            params = {
                "category": cat,
                "apiKey": NEWS_API_KEY,
                "language": "en",
                "pageSize": 10
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                articles = response.json().get("articles", [])
                news_data[cat] = articles
            await asyncio.sleep(0.5)  # Rate limit
        except:
            news_data[cat] = []
    
    return news_data

# ================= UI =================
def get_keyboard():
    keyboard = [
        [InlineKeyboardButton("📰 Technology", callback_data="technology")],
        [InlineKeyboardButton("⚽ Sports", callback_data="sports")],
        [InlineKeyboardButton("💼 Business", callback_data="business")],
        [InlineKeyboardButton("🎬 Entertainment", callback_data="entertainment")],
        [InlineKeyboardButton("🧬 Science", callback_data="science")],
        [InlineKeyboardButton("❤️ Health", callback_data="health")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🗞️ *News Bot Active*

Choose a category:",
        reply_markup=get_keyboard(),
        parse_mode="Markdown"
    )

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Fetching latest news...")
    
    try:
        data = await fetch_all_news()
        await asyncio.to_thread(save_news, data)
        await msg.edit_text("✅ News updated successfully!")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category = query.data
    news_list = await asyncio.to_thread(get_news_by_category, category)
    
    if not news_list:
        await query.edit_message_text("⚠️ No news available. Use /refresh first!")
        return
    
    text = f"📂 *{category.upper()} NEWS*

"
    
    for i, news in enumerate(news_list, 1):
        text += f"{i}. {news['headline']}
"
        text += f"🔗 {news['url']}

"
    
    if len(text) > 4000:
        text = text[:3990] + "..."
    
    await query.edit_message_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================= AUTO UPDATE =================
async def auto_update(context: ContextTypes.DEFAULT_TYPE):
    try:
        if not await asyncio.to_thread(is_today_data):
            print("🔄 Auto-updating news...")
            data = await fetch_all_news()
            await asyncio.to_thread(save_news, data)
            print("✅ Auto update complete")
    except Exception as e:
        print(f"❌ Auto-update error: {e}")

# ================= MAIN BOT =================
async def main():
    init_db()
    print("🚀 Starting News Telegram Bot...")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("refresh", refresh))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Auto-update every 4 hours (14400 seconds)
    app.job_queue.run_repeating(auto_update, interval=14400, first=10)
    
    print("✅ Bot started successfully!")
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
