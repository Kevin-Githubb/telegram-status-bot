import asyncio
import os
import time
from datetime import datetime, timedelta
from telegram.ext import ApplicationBuilder

# --- Bot token ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# --- Telegram chat & topic ---
GROUP_ID = -1003893865263
TOPIC_1_ID = 190  # Topic to poll

# --- Poll options ---
OPTIONS = ["Eating", "Going to Sleep", "Working", "Studying", "Exercising", "Washing Up"]

# Interval between polls (seconds)
POLL_INTERVAL = 15 * 60  # 15 minutes

# File to store last poll timestamp
LAST_POLL_FILE = "last_poll_time.txt"

# Allowed poll hours
START_HOUR = 7   # 7:00 AM
END_HOUR = 24    # Midnight

# Singleton task to prevent multiple loops
_poll_task = None

# ------------------ Utility Functions ------------------

def load_last_poll_time():
    """Load the timestamp of the last poll from file."""
    try:
        with open(LAST_POLL_FILE, "r") as f:
            return float(f.read())
    except Exception:
        return 0.0

def save_last_poll_time(ts):
    """Save the timestamp of the last poll to file."""
    try:
        with open(LAST_POLL_FILE, "w") as f:
            f.write(str(ts))
    except Exception as e:
        print(f"Error saving last poll time: {e}")

def seconds_until_next_allowed():
    """Return seconds until next allowed poll time if outside allowed hours."""
    now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        return 0
    # If before allowed hours
    next_start = now.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
    if now.hour >= END_HOUR:  # After midnight
        next_start += timedelta(days=1)
    return (next_start - now).total_seconds()

# ------------------ Polling Functions ------------------

async def send_poll(app):
    """Send a poll to Topic 1 and update last poll timestamp."""
    try:
        message = await app.bot.send_poll(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_1_ID,
            question="What is Kevin doing right now?",
            options=OPTIONS,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        print(f"[{datetime.now()}] Poll sent! Poll ID: {message.poll.id}, Message ID: {message.message_id}")
        save_last_poll_time(time.time())
    except Exception as e:
        print(f"Error sending poll: {e}")

async def poll_loop(app):
    """Main poll loop."""
    # Calculate initial wait based on last poll
    last_time = load_last_poll_time()
    now = time.time()
    wait_seconds = max(0, POLL_INTERVAL - (now - last_time))

    # Wait for allowed hours if outside window
    extra_wait = seconds_until_next_allowed()
    if extra_wait > 0:
        print(f"Outside allowed hours, waiting {extra_wait:.0f}s until next poll window...")
        await asyncio.sleep(extra_wait)

    # Wait remaining interval before first poll
    if wait_seconds > 0:
        print(f"Waiting {wait_seconds:.0f}s until next poll based on last timestamp...")
        await asyncio.sleep(wait_seconds)

    # Start loop
    while True:
        # Check allowed hours
        extra_wait = seconds_until_next_allowed()
        if extra_wait > 0:
            print(f"Outside allowed hours, sleeping {extra_wait:.0f}s...")
            await asyncio.sleep(extra_wait)

        await send_poll(app)
        await asyncio.sleep(POLL_INTERVAL)

async def start_poll(application):
    """Start the poll loop once."""
    global _poll_task
    if _poll_task is None:
        _poll_task = asyncio.create_task(poll_loop(application))

# ------------------ Main ------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # PTB calls this once after initialization
    app.post_init = start_poll
    print("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()