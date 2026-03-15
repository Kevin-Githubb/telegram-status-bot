import datetime
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = -1003893865263
TOPIC_STATUS = 190
TOPIC_PROMPT = 191

options = [
    "Working",
    "Studying",
    "Travelling",
    "Eating",
    "Sleeping",
    "Washing Up",
    "Others"
]

async def send_prompt(app):

    now = datetime.datetime.now()

    if 7 <= now.hour < 24:

        keyboard = [[InlineKeyboardButton(o, callback_data=o)] for o in options]

        await app.bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=TOPIC_PROMPT,
            text="Kevin, what are you doing?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    status = query.data

    await context.bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=TOPIC_STATUS,
        text=f"Kevin: {status}"
    )

async def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CallbackQueryHandler(button))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_prompt, "interval", minutes=15, args=[app])
    scheduler.start()

    await app.run_polling()

import asyncio
asyncio.run(main())