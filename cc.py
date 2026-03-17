import os
import requests
from flask import Flask
from threading import Thread
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import time

# ---------------- WEB SERVER ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 Ultimate News Bot Running"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
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

    r = requests.get(url)
    data = r.json()

    articles = data.get("articles", [])[:5]

    news = "📰 *Latest News*\n\n"

    for a in articles:
        news += f"{a['title']}\n{a['url']}\n\n"

    return news

# ---------------- COMMANDS ----------------
def start(update, context):
    update.message.reply_text(
        "🔥 Welcome to Ultimate News Bot\n\n"
        "Commands:\n"
        "/tech\n/sports\n/crypto\n/india\n/business"
    )

def tech(update, context):
    update.message.reply_text(fetch_news(category="technology"))

def sports(update, context):
    update.message.reply_text(fetch_news(category="sports"))

def india(update, context):
    update.message.reply_text(fetch_news())

def business(update, context):
    update.message.reply_text(fetch_news(category="business"))

def crypto(update, context):
    update.message.reply_text(fetch_news(query="crypto"))

# ---------------- AUTO NEWS SYSTEM ----------------
def auto_news(bot):
    while True:
        now = datetime.now()

        # Morning 8 AM
        if now.hour == 8 and now.minute == 0:
            bot.send_message(chat_id=CHAT_ID, text="🌅 Morning News\n\n" + fetch_news())

        # Every 6 hours
        if now.hour % 6 == 0 and now.minute == 0:
            bot.send_message(chat_id=CHAT_ID, text="⏰ Auto Update\n\n" + fetch_news())

        time.sleep(60)

# ---------------- BOT START ----------------
def start_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tech", tech))
    dp.add_handler(CommandHandler("sports", sports))
    dp.add_handler(CommandHandler("crypto", crypto))
    dp.add_handler(CommandHandler("india", india))
    dp.add_handler(CommandHandler("business", business))

    updater.start_polling()

    # Auto news thread
    Thread(target=auto_news, args=(updater.bot,)).start()

    updater.idle()

# ---------------- RUN ----------------
keep_alive()

Thread(target=start_bot).start()
