import os
import requests
from flask import Flask
from threading import Thread
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import time

# ---------------- FLASK WEB SERVER ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 Ultimate News Bot Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")
NEWS_API = os.getenv("NEWS_API")
CHAT_ID = os.getenv("CHAT_ID")

# ---------------- NEWS FUNCTION ----------------
def fetch_news(category=None, query=None):
    if category:
        url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={NEWS_API}"
    elif query:
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={NEWS_API}"
    else:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API}"

    try:
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

# ---------------- COMMANDS ----------------
def start(update, context):
    update.message.reply_text(
        "🔥 *Welcome to Ultimate News Bot*

"
        "*Commands:*
"
        "/tech - Technology news
"
        "/sports - Sports news
"
        "/business - Business news
"
        "/crypto - Crypto news
"
        "/india - India news"
    )

def tech(update, context):
    update.message.reply_text(fetch_news(category="technology"))

def sports(update, context):
    update.message.reply_text(fetch_news(category="sports"))

def business(update, context):
    update.message.reply_text(fetch_news(category="business"))

def crypto(update, context):
    update.message.reply_text(fetch_news(query="crypto"))

def india(update, context):
    update.message.reply_text(fetch_news())

# ---------------- AUTO NEWS ----------------
def auto_news(bot):
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            bot.send_message(chat_id=CHAT_ID, text="🌅 *Morning News*

" + fetch_news())
        if now.hour % 6 == 0 and now.minute == 0:
            bot.send_message(chat_id=CHAT_ID, text="⏰ *Auto Update*

" + fetch_news())
        time.sleep(60)

# ---------------- MAIN BOT ----------------
def start_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tech", tech))
    dp.add_handler(CommandHandler("sports", sports))
    dp.add_handler(CommandHandler("business", business))
    dp.add_handler(CommandHandler("crypto", crypto))
    dp.add_handler(CommandHandler("india", india))

    Thread(target=auto_news, args=(updater.bot,), daemon=True).start()
    updater.start_polling()
    updater.idle()

# ---------------- RUN EVERYTHING ----------------
if __name__ == "__main__":
    keep_alive()
    start_bot()
