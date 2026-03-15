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

def next_quarter_exact(now=None):
    """Return datetime object of the next quarter-hour in allowed hours."""
    if now is None:
        now = datetime.now()
    
    # Round up to the next quarter
    minutes = ((now.minute // 15) + 1) * 15
    hour = now.hour
    if minutes == 60:
        minutes = 0
        hour += 1
    next_quarter = now.replace(hour=hour, minute=minutes, second=0, microsecond=0)

    # If next_quarter is outside allowed hours, move to next day's START_HOUR
    if not (START_HOUR <= next_quarter.hour < END_HOUR):
        next_quarter = next_quarter.replace(hour=START_HOUR, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    return next_quarter

def seconds_until_next_quarter():
    """Return seconds until next poll time."""
    now = datetime.now()
    next_time = next_quarter_exact(now)
    delta = (next_time - now).total_seconds()
    return max(delta, 0)

# ------------------ Polling ------------------

async def send_poll(context):
    """Send a poll if within allowed hours."""
    now = datetime.now()
    if not (START_HOUR <= now.hour < END_HOUR):
        # Outside allowed hours, do nothing (next poll scheduled automatically)
        print(f"[{now}] Outside allowed hours. Skipping poll.")
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

# ------------------ Main ------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Calculate initial delay to align with next quarter-hour
    initial_wait = seconds_until_next_quarter()

    # Schedule repeating poll every 15 minutes
    app.job_queue.run_repeating(send_poll, interval=900, first=initial_wait)
    print(f"[{datetime.now()}] Bot starting... first poll in {initial_wait:.0f}s")

    app.run_polling()

if __name__ == "__main__":
    main()