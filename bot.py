import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = -1003893865263  # Supergroup
TOPIC_QUESTION = 191      # Topic 2
TOPIC_RESULT = 190        # Topic 1

options = ["Working", "Studying", "Sleeping", "Eating", "Travelling", "Washing up", "Others"]

# Add option dynamically via /addoption
async def addoption(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        new_opt = " ".join(context.args)
        if new_opt not in options:
            options.append(new_opt)
            await update.message.reply_text(f"Added option: {new_opt}")
        else:
            await update.message.reply_text(f"Option exists: {new_opt}")
    else:
        await update.message.reply_text("Usage: /addoption <option_name>")

# Handle button press
async def button_callback(update, context):
    query = update.callback_query
    await query.answer()
    await context.bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=TOPIC_RESULT,
        text=f"{query.from_user.first_name}: {query.data}"
    )

# Send question to Topic 2
async def send_question(application):
    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await application.bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=TOPIC_QUESTION,
        text="What are you doing?",
        reply_markup=reply_markup
    )

# Start the scheduler inside the running event loop
async def start_scheduler(application):
    scheduler = AsyncIOScheduler()
    # 7am to 11pm every 15 minutes
    scheduler.add_job(send_question, 'cron', hour='7-23', minute='0,15,30,45', args=[application])
    scheduler.start()
    logger.info("Scheduler started")

# Main bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CommandHandler("addoption", addoption))

    # Start scheduler inside bot loop using post_startup
    app.run_polling(post_startup=start_scheduler(app))

if __name__ == "__main__":
    main()