import os
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
OPTIONS = ["Eating", "Going to Sleep", "Working", "Studying", "Exercising", "Washing Up", "Travelling"]

# Allowed poll hours
START_HOUR = 7   # 7:00 AM
END_HOUR = 24    # Midnight

# ------------------ Utils ------------------

def next_quarter_now_or_future():
    """Return datetime object of the next quarter-hour in allowed hours."""
    now = datetime.now()
    # Round to the next quarter-hour
    minutes = (now.minute // 15) * 15
    next_quarter = now.replace(minute=minutes, second=0, microsecond=0)
    if now > next_quarter or now.minute % 15 != 0 or now.second != 0:
        next_quarter += timedelta(minutes=15)

    # If next_quarter is outside allowed hours, set to next START_HOUR
    if not (START_HOUR <= next_quarter.hour < END_HOUR):
        next_quarter = next_quarter.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
        if next_quarter <= now:
            next_quarter += timedelta(days=1)

    return next_quarter

def seconds_until_next_quarter():
    """Return seconds until next poll time."""
    now = datetime.now()
    next_time = next_quarter_now_or_future()
    delta = (next_time - now).total_seconds()
    return max(delta, 0)

# ------------------ Polling ------------------

async def send_poll(context):
    """Send a poll and schedule the next one at the next quarter-hour."""
    now = datetime.now()
    if not (START_HOUR <= now.hour < END_HOUR):
        # Wait until allowed hours
        next_quarter = next_quarter_now_or_future()
        wait_seconds = (next_quarter - now).total_seconds()
        context.job_queue.run_once(send_poll, wait_seconds)
        print(f"[{datetime.now()}] Outside allowed hours. Rescheduled poll in {wait_seconds:.0f}s")
        return

    try:
        message = await context.bot.send_poll(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_1_ID,
            question="What is Kevin doing right now?",
            options=OPTIONS,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        print(f"[{datetime.now()}] Poll sent! Poll ID: {message.poll.id}")
    except Exception as e:
        print(f"[{datetime.now()}] Error sending poll: {e}")

    # Schedule next poll
    next_quarter = next_quarter_now_or_future()
    wait_seconds = (next_quarter - datetime.now()).total_seconds()
    context.job_queue.run_once(send_poll, wait_seconds)
    print(f"[{datetime.now()}] Next poll scheduled in {wait_seconds:.0f}s")

# ------------------ Main ------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    initial_wait = seconds_until_next_quarter()
    app.job_queue.run_once(send_poll, initial_wait)
    print(f"[{datetime.now()}] Bot starting... first poll in {initial_wait:.0f}s")

    app.run_polling()

if __name__ == "__main__":
    main()