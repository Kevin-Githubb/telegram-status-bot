# bot.py
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variable for bot token
TOKEN = os.getenv("BOT_TOKEN")

# Telegram supergroup and topics
CHAT_ID = -1003893865263  # replace with your supergroup ID
TOPIC_QUESTION = 191       # Topic 2: ping you
TOPIC_RESULT = 190         # Topic 1: log your response

# Default options
options = ["Working", "Studying", "Sleeping", "Eating", "Travelling", "Washing up", "Others"]

# Command to add new options dynamically
async def addoption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        new_option = " ".join(context.args)
        if new_option not in options:
            options.append(new_option)
            await update.message.reply_text(f"Added new option: {new_option}")
        else:
            await update.message.reply_text(f"Option already exists: {new_option}")
    else:
        await update.message.reply_text("Usage: /addoption <option_name>")

# Callback when a button is pressed
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    status = query.data
    # Send to Topic 1
    await context.bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=TOPIC_RESULT,
        text=f"{query.from_user.first_name}: {status}"
    )

# Send options every 15 minutes to Topic 2
async def send_question(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=TOPIC_QUESTION,
        text="What are you doing?",
        reply_markup=reply_markup
    )

# Start scheduler
def start_scheduler(application):
    scheduler = AsyncIOScheduler()
    # 7:00 to 23:59, every 15 min
    scheduler.add_job(send_question, 'cron', hour='7-23', minute='0,15,30,45', args=[application])
    scheduler.start()

# Main bot startup
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CommandHandler("addoption", addoption))

    # Start scheduler
    start_scheduler(app)

    # Run polling (handles async loop correctly for Railway)
    app.run_polling()

if __name__ == "__main__":
    main()