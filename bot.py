import asyncio
import os
from telegram import Poll
from telegram.ext import ApplicationBuilder, ContextTypes

# --- Bot token ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# --- Telegram chat & topics ---
GROUP_ID = -1003893865263
TOPIC_1_ID = 190  # Topic to poll
TOPIC_2_ID = 191  # Topic to send results

# --- Poll options ---
OPTIONS = ["Eating", "Sleeping", "Working", "Exercising"]  # Customize as needed

# Interval between polls (seconds)
POLL_INTERVAL = 15 * 60  # 15 minutes


async def send_poll(app):
    """Send a poll to Topic 1 and return poll_id & message_id."""
    message = await app.bot.send_poll(
        chat_id=GROUP_ID,
        message_thread_id=TOPIC_1_ID,
        question="What are you doing right now?",
        options=OPTIONS,
        is_anonymous=False,
        allows_multiple_answers=False
    )
    return message.poll.id, message.message_id


async def poll_cycle(app):
    """Send a poll every POLL_INTERVAL seconds."""
    while True:
        try:
            poll_id, msg_id = await send_poll(app)
            print(f"Poll sent! Poll ID: {poll_id}, Message ID: {msg_id}")
        except Exception as e:
            print(f"Error sending poll: {e}")
        await asyncio.sleep(POLL_INTERVAL)


async def start_poll_loop(application):
    """
    Starts the poll cycle once. Sends the first poll immediately.
    Ensures only one task is created even if post_init fires multiple times.
    """
    if not getattr(application, "_poll_cycle_started", False):
        application._poll_cycle_started = True
        # Send first poll immediately
        await send_poll(application)
        # Start recurring poll loop
        asyncio.create_task(poll_cycle(application))


def main():
    # Create the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Assign post_init function to start poll loop
    app.post_init = start_poll_loop

    # Start bot (blocking)
    print("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()