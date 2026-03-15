import os
import asyncio
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, PollHandler, ContextTypes

# Bot token from environment
TOKEN = os.environ.get("BOT_TOKEN")

# Telegram IDs
GROUP_ID = -1003893865263
TOPIC_1_ID = 190  # User activity messages
TOPIC_2_ID = 191  # Poll options

# Users mapping
USER_MAP = {
    "iteachbad": "Kevin",
    "ilearnbad": "Giselle"
}

OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]

# Track poll data and responses
poll_data = {}

async def send_poll(app):
    """Send poll to topic 2 once"""
    message = await app.bot.send_poll(
        chat_id=GROUP_ID,
        question="Choose your current activity:",
        options=OPTIONS,
        type=Poll.REGULAR,
        is_anonymous=False,
        message_thread_id=TOPIC_2_ID,
    )
    poll_id = message.poll.id
    poll_data[poll_id] = {"message_id": message.message_id}
    print(f"Poll sent with id {poll_id}")
    return poll_id

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle answers from users"""
    poll_id = update.poll_answer.poll_id
    username = update.poll_answer.user.username
    option_ids = update.poll_answer.option_ids

    if poll_id not in poll_data:
        return

    if username in USER_MAP:
        poll_data[poll_id][username] = OPTIONS[option_ids[0]]

    # If both users responded, send activity messages and delete poll
    if all(u in poll_data[poll_id] for u in USER_MAP):
        for uname, display_name in USER_MAP.items():
            text = f"{display_name}: {poll_data[poll_id][uname]}"
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=text,
                message_thread_id=TOPIC_1_ID
            )
        await context.bot.delete_message(
            chat_id=GROUP_ID,
            message_id=poll_data[poll_id]["message_id"],
            message_thread_id=TOPIC_2_ID
        )
        del poll_data[poll_id]

async def poll_cycle(app):
    """Send poll every 15 minutes"""
    while True:
        await send_poll(app)
        await asyncio.sleep(900)  # wait 15 minutes

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(PollHandler(handle_poll_answer))

    # Start the polling cycle task
    asyncio.create_task(poll_cycle(app))

    print("Bot starting...")
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # Already running loop (common in some environments)
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()