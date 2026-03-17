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

# ================= WEB SERVER =================
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot Running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

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
        "🗞️ Choose a category:",
        reply_markup=get_keyboard()
    )

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Fetching latest news...")

    try:
        data = await asyncio.to_thread(fetch_all_news)
        await asyncio.to_thread(save_news, data)
        await msg.edit_text("✅ News updated!")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

# ================= BUTTON =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data
    news_list = get_news_by_category(category)

    if not news_list:
        await query.edit_message_text("⚠️ No news. Use /refresh")
        return

    text = f"📂 {category.upper()} NEWS\n\n"

    for news in news_list[:5]:
        text += (
            f"📰 {news.get('headline')}\n"
            f"🔗 {news.get('url')}\n\n"
        )

    await query.edit_message_text(text[:4000])

# ================= AUTO UPDATE =================
async def auto_update(context: ContextTypes.DEFAULT_TYPE):
    try:
        if not is_today_data():
            data = await asyncio.to_thread(fetch_all_news)
            await asyncio.to_thread(save_news, data)
            print("✅ Auto updated")
    except Exception as e:
        print("Error:", e)

# ================= BOT =================
def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("refresh", refresh))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.job_queue.run_repeating(auto_update, interval=21600, first=10)

    print("🚀 Bot started")
    app.run_polling(close_loop=False)

# ================= START =================
if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    run_bot()
