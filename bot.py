import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    PollHandler,
)

# --- Bot token ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# --- Group and threads ---
GROUP_ID = -1003893865263
TOPIC_1_THREAD_ID = 190  # Poll goes here
TOPIC_2_THREAD_ID = 191  # Forward answers here

# --- Poll options ---
OPTIONS = ["Eating", "Sleeping", "Working", "Exercising"]

# --- Interval between polls (seconds) ---
POLL_INTERVAL = 15 * 60  # 15 minutes


async def send_poll(bot):
    """Send a poll to Topic 1."""
    message = await bot.send_poll(
        chat_id=GROUP_ID,
        message_thread_id=TOPIC_1_THREAD_ID,
        question="What are you doing right now?",
        options=OPTIONS,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    print(f"Poll sent! Poll ID: {message.poll.id}")


async def poll_cycle(app):
    """Send polls repeatedly every POLL_INTERVAL seconds."""
    while True:
        try:
            await send_poll(app.bot)
        except Exception as e:
            print(f"Error sending poll: {e}")
        await asyncio.sleep(POLL_INTERVAL)


async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward answers from Topic 1 to Topic 2."""
    user = update.poll_answer.user
    option_ids = update.poll_answer.option_ids
    chosen_options = [OPTIONS[i] for i in option_ids]

    text = f"{user.full_name} chose: {', '.join(chosen_options)}"
    await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=TOPIC_2_THREAD_ID,
        text=text
    )
    print(f"Forwarded poll answer to Topic 2: {text}")


async def start_polling_loop(application):
    """Start the automated poll cycle when the bot starts."""
    asyncio.create_task(poll_cycle(application))


def main():
    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add poll answer handler
    app.add_handler(PollHandler(handle_poll_answer))

    # Start automated polling immediately
    app.post_init = start_polling_loop

    print("Bot starting and poll cycle running...")
    # This runs the bot and manages the asyncio loop internally
    app.run_polling()


if __name__ == "__main__":
    main()