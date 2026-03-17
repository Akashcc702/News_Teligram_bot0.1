import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from news_fetcher import fetch_all_news
from storage import save_news, get_news_by_category

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ---------------- WEB SERVER ----------------
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot Running 🚀"


# ---------------- KEYBOARD ----------------
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📰 Technology", callback_data="technology")],
        [InlineKeyboardButton("⚽ Sports", callback_data="sports")],
        [InlineKeyboardButton("💼 Business", callback_data="business")],
        [InlineKeyboardButton("🎬 Entertainment", callback_data="entertainment")],
        [InlineKeyboardButton("🧬 Science", callback_data="science")],
        [InlineKeyboardButton("❤️ Health", callback_data="health")]
    ])


# ---------------- COMMANDS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🗞️ Select category:",
        reply_markup=get_keyboard()
    )


async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Fetching news...")

    # run blocking code in thread
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, fetch_all_news)

    save_news(data)

    await msg.edit_text("✅ News updated!")


# ---------------- BUTTON HANDLER ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data
    news_list = get_news_by_category(category)

    if not news_list:
        await query.edit_message_text("⚠️ No news. Use /refresh")
        return

    text = f"📂 {category.upper()} NEWS\n\n"

    for n in news_list[:5]:
        text += (
            f"📰 {n['headline']}\n"
            f"✏️ {n['summary'][:200]}...\n"
            f"🔗 {n['url']}\n\n"
        )

    await query.edit_message_text(text[:4000])


# ---------------- AUTO UPDATE ----------------
async def auto_update(app):
    while True:
        try:
            print("🔄 Auto updating news...")

            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(None, fetch_all_news)

            save_news(data)

            print("✅ Updated successfully")

        except Exception as e:
            print("❌ Auto अपडेट error:", e)

        await asyncio.sleep(21600)  # 6 hours


# ---------------- MAIN ----------------
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("refresh", refresh))
    app.add_handler(CallbackQueryHandler(button_handler))

    # start auto-update task
    app.create_task(auto_update(app))

    print("🚀 Bot started...")
    await app.run_polling()


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    Thread(target=run_web).start()
    asyncio.run(main())
