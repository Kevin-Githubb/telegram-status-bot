import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "YOUR_BOT_TOKEN"

options = ["Working", "Studying", "Eating", "Travelling", "Sleeping", "Other"]
topic1_id = -1003893865263  # Where responses go
topic2_id = -1003893865263  # Where the bot pings you (can be same supergroup, different thread)

scheduler = AsyncIOScheduler()

# Ping function
async def ping(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=topic2_id,
        text="What are you doing?",
        reply_markup=reply_markup
    )

# Handle button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    response = query.data
    await context.bot.send_message(
        chat_id=topic1_id,
        text=f"{query.from_user.first_name}: {response}"
    )

async def start_scheduler(app):
    scheduler.add_job(lambda: asyncio.create_task(ping(app.bot)), 'interval', minutes=15,
                      start_date='2026-03-15 07:00:00', end_date='2026-03-15 23:59:00')
    scheduler.start()

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CallbackQueryHandler(button))

    # Start scheduler after bot starts
    asyncio.create_task(start_scheduler(app))

    # Run bot
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())