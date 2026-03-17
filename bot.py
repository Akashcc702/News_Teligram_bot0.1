import os
import requests
from flask import Flask
from threading import Thread
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import time

# Flask Web Server
app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 Ultimate News Bot v2.0 Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

# Config
TOKEN = os.getenv("BOT_TOKEN")
NEWS_API = os.getenv("NEWS_API")
CHAT_ID = os.getenv("CHAT_ID")

# News Function
def fetch_news(category=None, query=None):
    try:
        if category:
            url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={NEWS_API}"
        elif query:
            url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={NEWS_API}"
        else:
            url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API}"

        r = requests.get(url, timeout=10)
        data = r.json()
        articles = data.get("articles", [])[:5]
        
        news = "📰 *Latest News*

"
        for a in articles:
            news += f"📢 {a['title']}
🔗 {a['url']}

"
        return news if articles else "❌ No news found"
    except:
        return "❌ News fetch failed"

# Command Handlers (v20 syntax)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *Welcome to Ultimate News Bot*

"
        "*Commands:*
/tech
/sports
/business
/crypto
/india"
    )

async def tech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news(category="technology"))

async def sports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news(category="sports"))

async def business(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news(category="business"))

async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news(query="crypto"))

async def india(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news())

# Auto News
async def auto_news(app):
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            await app.bot.send_message(chat_id=CHAT_ID, text="🌅 *Morning News*

" + fetch_news())
        if now.hour % 6 == 0 and now.minute == 0:
            await app.bot.send_message(chat_id=CHAT_ID, text="⏰ *Auto Update*

" + fetch_news())
        await asyncio.sleep(60)

# Main Bot
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CommandHandler("sports", sports))
    app.add_handler(CommandHandler("business", business))
    app.add_handler(CommandHandler("crypto", crypto))
    app.add_handler(CommandHandler("india", india))

    # Auto news task
    asyncio.create_task(auto_news(app))
    
    await app.run_polling()

# Run Everything
if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
