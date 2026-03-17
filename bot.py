import os
import requests
from flask import Flask
from threading import Thread
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import time

# Flask Keep-Alive Server
app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 News Telegram Bot Running Successfully!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

def keep_alive():
    Thread(target=run_flask, daemon=True).start()

# Config
TOKEN = os.getenv("BOT_TOKEN")
NEWS_API = os.getenv("NEWS_API")
CHAT_ID = os.getenv("CHAT_ID")

# News Function (Thread-Safe)
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
        
        if not articles:
            return "❌ No news available"
            
        news = "📰 *Latest News*

"
        for a in articles:
            news += f"📢 {a.get('title', 'No title')}
🔗 {a.get('url', 'No URL')}

"
        return news
    except Exception as e:
        return f"❌ News fetch error: {str(e)[:50]}"

# Bot Commands (v20 async)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *Ultimate News Bot*

"
        "Commands:
"
        "/tech
/sports
/business
/crypto
/india"
    )

async def tech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news("technology"))

async def sports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news("sports"))

async def business(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news("business"))

async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news(query="bitcoin"))

async def india(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_news())

# SIMPLE AUTO NEWS (Thread-based, NO asyncio issues)
def auto_news_loop(bot):
    while True:
        try:
            now = datetime.now()
            if now.hour == 8 and now.minute == 0:
                asyncio.run_coroutine_threadsafe(
                    bot.send_message(chat_id=CHAT_ID, text="🌅 *Morning News*

" + fetch_news()),
                    asyncio.get_event_loop()
                )
            if now.hour % 6 == 0 and now.minute == 0:
                asyncio.run_coroutine_threadsafe(
                    bot.send_message(chat_id=CHAT_ID, text="⏰ *Auto Update*

" + fetch_news()),
                    asyncio.get_event_loop()
                )
            time.sleep(60)
        except:
            time.sleep(60)

# Main Bot Function
async def main():
    print("🚀 Starting Telegram Bot...")
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tech", tech))
    application.add_handler(CommandHandler("sports", sports))
    application.add_handler(CommandHandler("business", business))
    application.add_handler(CommandHandler("crypto", crypto))
    application.add_handler(CommandHandler("india", india))

    # Start auto news in background thread
    Thread(target=auto_news_loop, args=(application.bot,), daemon=True).start()
    
    print("✅ Bot started successfully!")
    await application.run_polling(drop_pending_updates=True)

# RUN EVERYTHING
if __name__ == "__main__":
    if not all([TOKEN, NEWS_API, CHAT_ID]):
        print("❌ Missing environment variables!")
        exit(1)
    
    print("Starting Flask + Telegram Bot...")
    keep_alive()  # Flask server
    asyncio.run(main())  # Telegram bot
