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
OPTIONS = ["Eating", "Going to Sleep", "Working", "Studying", "Exercising", "Washing Up","Travelling"]

# Allowed poll hours
START_HOUR = 7   # 7:00 AM
END_HOUR = 24    # Midnight

# ------------------ Utils ------------------

def seconds_until_next_allowed():
    """Return seconds until next allowed poll time if outside allowed hours."""
    now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        return 0
    # Wait until next START_HOUR
    next_start = now.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
    if now.hour >= END_HOUR or now.hour < START_HOUR:
        if now.hour >= END_HOUR:
            next_start += timedelta(days=1)
    delta = (next_start - now).total_seconds()
    return max(delta, 0)

def seconds_until_next_quarter():
    """Return seconds until the next quarter-hour mark (00, 15, 30, 45)."""
    now = datetime.now()
    # Compute next quarter-hour minute
    next_minute = (now.minute // 15 + 1) * 15
    next_time = now.replace(second=0, microsecond=0)
    if next_minute >= 60:
        # move to next hour
        next_time = next_time.replace(minute=0) + timedelta(hours=1)
    else:
        next_time = next_time.replace(minute=next_minute)
    # Make sure it's in allowed hours
    extra_wait = seconds_until_next_allowed()
    delta = (next_time - now).total_seconds()
    return max(delta, extra_wait)

# ------------------ Polling ------------------

async def send_poll(context):
    """Send a poll and schedule the next one at the next quarter-hour."""
    # Check allowed hours
    extra_wait = seconds_until_next_allowed()
    if extra_wait > 0:
        # Reschedule at allowed time
        context.job_queue.run_once(send_poll, extra_wait)
        print(f"[{datetime.now()}] Outside allowed hours. Rescheduled poll in {extra_wait:.0f}s")
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

    # Schedule next poll at next quarter-hour
    next_quarter = seconds_until_next_quarter()
    context.job_queue.run_once(send_poll, next_quarter)
    print(f"[{datetime.now()}] Next poll scheduled in {next_quarter:.0f}s")

# ------------------ Main ------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Schedule the first poll at the next quarter-hour
    initial_wait = seconds_until_next_quarter()
    app.job_queue.run_once(send_poll, initial_wait)
    print(f"[{datetime.now()}] Bot starting... first poll in {initial_wait:.0f}s")

    app.run_polling()

if __name__ == "__main__":
    main()