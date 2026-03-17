import os
import requests
from flask import Flask
from threading import Thread
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import time

# Flask server
app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 Bot Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

flask_thread = Thread(target=run_flask, daemon=True)

# Get ENV (default empty)
TOKEN = os.getenv("BOT_TOKEN", "")
NEWS_API = os.getenv("NEWS_API", "")
CHAT_ID = os.getenv("CHAT_ID", "")

def fetch_news():
    if not NEWS_API:
        return "❌ NewsAPI key missing"
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API}"
        r = requests.get(url, timeout=10)
        data = r.json()
        articles = data.get("articles", [])
        
        news = "📰 *LATEST NEWS*

"
        for i, a in enumerate(articles[:3], 1):
            news += f"{i}. {a.get('title', 'No title')}
"
            news += f"🔗 {a.get('url', '')}

"
        return news
    except:
        return "❌ News fetch failed"

# Commands
def start(update, context):
    update.message.reply_text(
        "🔥 NEWS BOT WORKING!

/tech
/sports
/india"
    )

def tech(update, context):
    update.message.reply_text(fetch_news())

def india(update, context):
    update.message.reply_text(fetch_news())

# Auto news (disabled if no CHAT_ID)
def auto_news(bot):
    if not CHAT_ID:
        return
    while True:
        time.sleep(3600)  # 1 hour

# Main
def main():
    if not TOKEN:
        print("⚠️ No BOT_TOKEN - bot commands disabled")
        flask_thread.start()
        while True:
            time.sleep(60)
        return
    
    print("🚀 Bot starting...")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tech", tech))
    dp.add_handler(CommandHandler("india", india))
    
    flask_thread.start()
    updater.start_polling()
    print("✅ Bot running!")
    Thread(target=auto_news, args=(updater.bot,), daemon=True).start()
    updater.idle()

if __name__ == "__main__":
    main()
