import asyncio
import os
from telegram.ext import ApplicationBuilder

# --- Bot token ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# --- Telegram chat & topic ---
GROUP_ID = -1003893865263
TOPIC_1_ID = 190  # Topic to poll

# --- Poll options ---
OPTIONS = ["Eating", "Sleeping", "Working", "Exercising"]

# Interval between polls (seconds)
POLL_INTERVAL = 15 * 60  # 15 minutes


async def send_poll(app):
    """Send a poll to Topic 1."""
    try:
        message = await app.bot.send_poll(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_1_ID,
            question="What are you doing right now?",
            options=OPTIONS,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        print(f"Poll sent! Poll ID: {message.poll.id}, Message ID: {message.message_id}")
    except Exception as e:
        print(f"Error sending poll: {e}")


async def poll_loop(app):
    """Send a poll immediately, then every POLL_INTERVAL seconds."""
    while True:
        await send_poll(app)           # send immediately
        await asyncio.sleep(POLL_INTERVAL)  # wait 15 minutes


async def start_poll(application):
    """Start the poll loop once."""
    if not getattr(application, "_poll_started", False):
        application._poll_started = True
        asyncio.create_task(poll_loop(application))


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Start the poll loop after app initializes
    app.post_init = start_poll

    print("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()