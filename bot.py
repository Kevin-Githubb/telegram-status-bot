import os
import time
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import Bot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

GROUP_ID = -1003893865263
TOPIC_1_ID = 190
OPTIONS = ["Eating", "Going to Sleep", "Working", "Studying", "Exercising", "Washing Up", "Travelling"]

START_HOUR = 7
END_HOUR = 24
TIMEZONE = ZoneInfo("Asia/Singapore")

# ------------------ Utils ------------------

def now_sgt():
    return datetime.now(TIMEZONE)

def next_quarter_after(now=None):
    if now is None:
        now = now_sgt()
    
    minutes = ((now.minute // 15) + 1) * 15
    hour = now.hour
    if minutes == 60:
        minutes = 0
        hour += 1
    next_quarter = now.replace(hour=hour, minute=minutes, second=0, microsecond=0)

    if not (START_HOUR <= next_quarter.hour < END_HOUR):
        next_quarter = now.replace(hour=START_HOUR, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    if next_quarter <= now:
        next_quarter += timedelta(minutes=15)
        if next_quarter.hour >= END_HOUR:
            next_quarter = next_quarter.replace(hour=START_HOUR, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    return next_quarter

def seconds_until(dt):
    return max((dt - now_sgt()).total_seconds(), 0)

# ------------------ Polling ------------------

def send_poll(bot: Bot, to_topic=True):
    now = now_sgt()
    if START_HOUR <= now.hour < END_HOUR:
        try:
            if to_topic:
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
                print(f"[{now}] Poll sent to topic {TOPIC_1_ID}")
            else:
                # first poll goes to main group without topic
                asyncio.run(
                    bot.send_poll(
                        chat_id=GROUP_ID,
                        question="What is Kevin doing right now?",
                        options=OPTIONS,
                        is_anonymous=False,
                        allows_multiple_answers=False
                    )
                )
                print(f"[{now}] First poll sent to group")
        except Exception as e:
            print(f"[{now}] Failed to send poll: {e}")
    else:
        print(f"[{now}] Outside allowed hours. Poll skipped")

# ------------------ Main ------------------

def main():
    bot = Bot(token=BOT_TOKEN)
    print(f"[{now_sgt()}] Bot started, sending first poll immediately")
    
    # First poll immediately to group (no topic)
    send_poll(bot, to_topic=False)
    time.sleep(1)  # tiny delay to prevent Telegram double-send

    while True:
        now = now_sgt()
        next_poll_time = next_quarter_after(now)
        wait_seconds = seconds_until(next_poll_time)
        print(f"[{now}] Waiting {wait_seconds:.0f}s until next poll at {next_poll_time}")
        time.sleep(wait_seconds)
        send_poll(bot, to_topic=True)  # subsequent polls to forum topic

if __name__ == "__main__":
    main()