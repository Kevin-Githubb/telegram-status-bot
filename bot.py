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
    message = await app.bot.send_poll(
        chat_id=GROUP_ID,
        message_thread_id=TOPIC_1_ID,
        question="What are you doing right now?",
        options=OPTIONS,
        is_anonymous=False,
        allows_multiple_answers=False
    )
    print(f"Poll sent! Poll ID: {message.poll.id}, Message ID: {message.message_id}")


async def poll_cycle(app):
    """Send a poll every POLL_INTERVAL seconds."""
    while True:
        try:
            await send_poll(app)
        except Exception as e:
            print(f"Error sending poll: {e}")
        await asyncio.sleep(POLL_INTERVAL)


async def start_poll_loop(application):
    """Start the recurring poll loop once."""
    if not getattr(application, "_poll_cycle_started", False):
        application._poll_cycle_started = True
        asyncio.create_task(poll_cycle(application))  # no immediate first poll, just loop


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Assign post_init to start the poll loop
    app.post_init = start_poll_loop

    print("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()