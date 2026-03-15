import os
import asyncio
from telegram import Poll, Update
from telegram.ext import ApplicationBuilder, PollHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
GROUP_ID = -1003893865263
TOPIC_1_ID = 190
TOPIC_2_ID = 191

OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]
USER_MAP = {"iteachbad": "Kevin", "ilearnbad": "Giselle"}
poll_data = {}


async def send_poll(app):
    if poll_data:
        return  # Only one poll at a time

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


async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_id = update.poll_answer.poll_id
    username = update.poll_answer.user.username
    option_ids = update.poll_answer.option_ids

    if poll_id not in poll_data or username not in USER_MAP:
        return

    poll_data[poll_id][username] = OPTIONS[option_ids[0]]

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
    """Send poll immediately and then every 15 minutes if none active"""
    while True:
        await send_poll(app)
        await asyncio.sleep(15 * 60)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(PollHandler(handle_poll_answer))

    print("Bot starting...")

    # Schedule the poll loop AFTER the bot is ready
    async def start_poll_loop():
        asyncio.create_task(poll_cycle(app))

    # PTB v20+ way to add post-start tasks:
    app.post_init = start_poll_loop  # <-- assign the coroutine, do NOT pass to run_polling()

    app.run_polling()  # no post_init argument here!


if __name__ == "__main__":
    main()