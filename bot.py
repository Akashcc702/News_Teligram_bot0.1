import os
import requests
from flask import Flask
from threading import Thread
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from datetime import datetime
import time

# Flask Keep-Alive (Render-ಗೆ must)
app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 News Bot Running! ✅"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Start Flask in background
flask_thread = Thread(target=run_flask, daemon=True)

# Config
TOKEN = os.getenv("BOT_TOKEN")
NEWS_API = os.getenv("NEWS_API")
CHAT_ID = os.getenv("CHAT_ID")

def fetch_news(category=None, query=None):
    try:
        if category:
            url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={NEWS_API}"
        elif query:
            url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API}"
        else:
            url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API}"

        r = requests.get(url, timeout=10)
        data = r.json()
        articles = data.get("articles", [])
        
        if not articles:
            return "❌ No news found"
            
        news = "📰 *TODAY'S NEWS*

"
        for i, a in enumerate(articles[:5], 1):
            news += f"{i}. {a.get('title', 'No title')}
"
            news += f"🔗 {a.get('url', 'No URL')}

"
        return news
    except:
        return "❌ News service temporarily unavailable"

# Bot Commands (v13 syntax - NO ASYNC)
def start(update, context):
    update.message.reply_text(
        "🔥 *ULTIMATE NEWS BOT*

"
        "📱 *Commands:*
"
        "/india - India News
"
        "/tech - Tech News
"
        "/sports - Sports
"
        "/business - Business
"
        "/crypto - Crypto News"
    )

def tech(update, context):
    update.message.reply_text(fetch_news("technology"))

def sports(update, context):
    update.message.reply_text(fetch_news("sports"))

def business(update, context):
    update.message.reply_text(fetch_news("business"))

def crypto(update, context):
    update.message.reply_text(fetch_news(query="cryptocurrency"))

def india(update, context):
    update.message.reply_text(fetch_news())

# Auto News (Simple Thread - NO asyncio)
def auto_news(bot):
    last_sent = {}
    while True:
        now = datetime.now()
        
        # Morning 8 AM
        if now.hour == 8 and now.minute == 0 and now.day != last_sent.get('morning', 0):
            bot.send_message(chat_id=CHAT_ID, text="🌅 *GOOD MORNING! TODAY'S NEWS*

" + fetch_news())
            last_sent['morning'] = now.day
            
        # Every 6 hours
        if now.hour % 6 == 0 and now.minute == 0:
            bot.send_message(chat_id=CHAT_ID, text="⏰ *NEWS UPDATE*

" + fetch_news())
            
        time.sleep(60)

# Main Bot Setup
def main():
    print("🚀 Starting News Bot...")
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tech", tech))
    dp.add_handler(CommandHandler("sports", sports))
    dp.add_handler(CommandHandler("business", business))
    dp.add_handler(CommandHandler("crypto", crypto))
    dp.add_handler(CommandHandler("india", india))
    
    # Start bot
    updater.start_polling(drop_pending_updates=True)
    print("✅ Bot started successfully!")
    
    # Auto news thread
    Thread(target=auto_news, args=(updater.bot,), daemon=True).start()
    
    # Keep running
    updater.idle()

# RUN EVERYTHING
if __name__ == "__main__":
    if not TOKEN or not NEWS_API or not CHAT_ID:
        print("❌ ERROR: Missing BOT_TOKEN, NEWS_API, or CHAT_ID")
        exit(1)
    
    print("🎯 Starting Flask + Telegram Bot...")
    flask_thread.start()  # Flask server
    main()               # Telegram bot
