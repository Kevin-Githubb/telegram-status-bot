import os
import time
from datetime import datetime, timedelta
from telegram import Bot
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

GROUP_ID = -1003893865263
TOPIC_1_ID = 190
OPTIONS = ["Eating", "Going to Sleep", "Working", "Studying", "Exercising", "Washing Up", "Travelling"]
START_HOUR = 7
END_HOUR = 24

# ------------------ Utils ------------------

def next_quarter_after(now=None):
    """Return the next quarter-hour strictly after `now`."""
    if now is None:
        now = datetime.now()
    minutes = ((now.minute // 15) + 1) * 15
    hour = now.hour
    if minutes == 60:
        minutes = 0
        hour += 1
    next_quarter = now.replace(hour=hour, minute=minutes, second=0, microsecond=0)
    if next_quarter <= now:
        next_quarter += timedelta(minutes=15)
    return next_quarter

def next_allowed_time(now=None):
    if now is None:
        now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        return now
    next_time = now.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
    if next_time <= now:
        next_time += timedelta(days=1)
    return next_time

def seconds_until(dt):
    return max((dt - datetime.now()).total_seconds(), 0)

# ------------------ Polling ------------------

def send_poll(bot: Bot):
    now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        try:
            asyncio.run(
                bot.send_poll(
                    chat_id=GROUP_ID,
                    message_thread_id=TOPIC_1_ID,
                    question="What is Kevin doing right now?",
                    options=OPTIONS,
                    is_anonymous=False,
                    allows_multiple_answers=False
                )
            )
            print(f"[{datetime.now()}] Poll sent to topic {TOPIC_1_ID}")
        except Exception as e:
            print(f"[{datetime.now()}] Failed to send poll: {e}")
    else:
        print(f"[{datetime.now()}] Outside allowed hours. Poll skipped.")

# ------------------ Main ------------------

def main():
    bot = Bot(token=BOT_TOKEN)
    print(f"[{datetime.now()}] Bot started, sending first poll immediately")
    
    # First poll immediately
    send_poll(bot)

    while True:
        now = datetime.now()
        # If outside allowed hours, sleep until next START_HOUR
        if not (START_HOUR <= now.hour < END_HOUR):
            next_time = next_allowed_time(now)
            wait_seconds = seconds_until(next_time)
            print(f"[{datetime.now()}] Sleeping until {next_time} ({wait_seconds:.0f}s)")
            time.sleep(wait_seconds)
            continue

        # Sleep until next quarter AFTER now
        next_quarter = next_quarter_after(now)
        wait_seconds = seconds_until(next_quarter)
        print(f"[{datetime.now()}] Waiting {wait_seconds:.0f}s until next poll at {next_quarter}")
        time.sleep(wait_seconds)
        send_poll(bot)

if __name__ == "__main__":
    main()