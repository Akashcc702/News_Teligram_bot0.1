import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from news_fetcher import fetch_all_news
from storage import save_news, get_news_by_category, is_today_data

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app_web = Flask(__name__)


@app_web.route("/")
def home():
    return "News Bot Running 🚀"


# ================= BOT UI =================

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🗞️ Choose a category:",
        reply_markup=get_keyboard()
    )


async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Fetching latest news...")

    data = fetch_all_news()
    save_news(data)

    await msg.edit_text("✅ News updated successfully!")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data
    news_list = get_news_by_category(category)

    if not news_list:
        await query.edit_message_text("⚠️ No news available. Try /refresh")
        return

    response = f"📂 {category.upper()} NEWS\n\n"

    for news in news_list[:5]:
        response += (
            f"📰 {news['headline']}\n"
            f"✏️ {news['summary']}\n"
            f"🔗 {news['url']}\n\n"
        )

    await query.edit_message_text(response[:4000])


# ================= AUTO UPDATE =================

async def auto_update():
    while True:
        if not is_today_data():
            data = fetch_all_news()
            save_news(data)
        await asyncio.sleep(21600)  # 6 hours


# ================= MAIN =================

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("refresh", refresh))
    app.add_handler(CallbackQueryHandler(button_handler))

    loop = asyncio.get_event_loop()
    loop.create_task(auto_update())

    app.run_polling()


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    Thread(target=run_web).start()
    run_bot()
