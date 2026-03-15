import os
import asyncio
from telegram import Poll, Update
from telegram.ext import ApplicationBuilder, PollHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

GROUP_ID = -1003893865263
TOPIC_1_ID = 190  # activity text
TOPIC_2_ID = 191  # poll options

USER_MAP = {"iteachbad": "Kevin", "ilearnbad": "Giselle"}
OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]

poll_data = {}  # poll_id -> {message_id, user responses}


async def send_poll(app):
    """Send a single poll if none active"""
    if poll_data:
        return  # already a poll active

    message = await app.bot.send_poll(
        chat_id=GROUP_ID,
        question="Choose your current activity:",
        options=OPTIONS,
        type=Poll.REGULAR,
        is_anonymous=False,
        message_thread_id=TOPIC_2_ID
    )
    poll_id = message.poll.id
    poll_data[poll_id] = {"message_id": message.message_id}
    print(f"Poll sent with id {poll_id}")
    return poll_id


async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_id = update.poll_answer.poll_id
    username = update.poll_answer.user.username
    option_ids = update.poll_answer.option_ids

    if poll_id not in poll_data or username not in USER_MAP:
        return

    poll_data[poll_id][username] = OPTIONS[option_ids[0]]

    # If all tracked users answered, post messages and delete poll
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
        poll_data.clear()


async def poll_cycle(app):
    """Send poll immediately on deploy and then every 15 minutes if no active poll"""
    while True:
        await send_poll(app)
        await asyncio.sleep(15 * 60)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(PollHandler(handle_poll_answer))

    print("Bot starting...")

    # Start the poll loop in the background after the app starts
    async def start_loop():
        asyncio.create_task(poll_cycle(app))

    # Use `run_polling` directly, don't wrap in asyncio.run()
    app.run_polling(post_init=start_loop if hasattr(app, "run_polling") else None)


if __name__ == "__main__":
    main()