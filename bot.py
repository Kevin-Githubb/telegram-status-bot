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
OPTIONS = ["Eating", "Going to Sleep", "Working", "Studying", "Exercising","Washing Up"]

# Interval between polls (seconds)
POLL_INTERVAL = 15 * 60  # 15 minutes

# File to store last poll timestamp
LAST_POLL_FILE = "last_poll_time.txt"

# Allowed poll hours
START_HOUR = 7   # 7:00 AM
END_HOUR = 24    # Midnight

# Flag to ensure single poll loop
_poll_task_started = False

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
    """Calculate seconds until the next allowed poll time if outside hours."""
    now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        return 0
    # If before 7 AM, wait until 7 AM
    next_start = now.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
    if now.hour >= END_HOUR:  # after midnight
        next_start += timedelta(days=1)
    return (next_start - now).total_seconds()

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
        print(f"Poll sent! Poll ID: {message.poll.id}, Message ID: {message.message_id}")
        save_last_poll_time(time.time())
    except Exception as e:
        print(f"Error sending poll: {e}")

async def poll_loop(app):
    """Send first poll based on last timestamp, then repeat every POLL_INTERVAL seconds."""
    last_time = load_last_poll_time()
    now = time.time()
    wait_seconds = max(0, POLL_INTERVAL - (now - last_time))

    # Wait until allowed hours if necessary
    extra_wait = seconds_until_next_allowed()
    if extra_wait > 0:
        print(f"Outside allowed hours, waiting {extra_wait:.0f}s until next poll window...")
        await asyncio.sleep(extra_wait)

    # Wait remaining interval
    if wait_seconds > 0:
        await asyncio.sleep(wait_seconds)

    while True:
        # Check time window
        extra_wait = seconds_until_next_allowed()
        if extra_wait > 0:
            print(f"Outside allowed hours, sleeping {extra_wait:.0f}s...")
            await asyncio.sleep(extra_wait)

        await send_poll(app)
        await asyncio.sleep(POLL_INTERVAL)

async def start_poll(application):
    """Start the poll loop only once after initialization."""
    global _poll_task_started
    if _poll_task_started:
        return
    _poll_task_started = True
    loop = asyncio.get_running_loop()
    loop.create_task(poll_loop(application))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.post_init = start_poll  # PTB calls this once after app initializes
    print("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()