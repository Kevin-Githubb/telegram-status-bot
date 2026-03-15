import os
import time
from datetime import datetime, timedelta
from telegram import Bot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

GROUP_ID = -1003893865263
TOPIC_1_ID = 190  # Make sure this is correct
OPTIONS = ["Eating", "Going to Sleep", "Working", "Studying", "Exercising", "Washing Up", "Travelling"]
START_HOUR = 7
END_HOUR = 24

def next_quarter_exact(now=None):
    if now is None:
        now = datetime.now()
    minutes = ((now.minute // 15) + 1) * 15
    hour = now.hour
    if minutes == 60:
        minutes = 0
        hour += 1
    return now.replace(hour=hour, minute=minutes, second=0, microsecond=0)

def next_allowed_time(now=None):
    if now is None:
        now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        return now
    next_time = now.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
    if next_time <= now:
        next_time += timedelta(days=1)
    return next_time

def seconds_until(next_time):
    return max((next_time - datetime.now()).total_seconds(), 0)

def send_poll(bot: Bot):
    now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        try:
            # Try sending to topic first
            bot.send_poll(
                chat_id=GROUP_ID,
                message_thread_id=TOPIC_1_ID,  # remove this if topic ID is invalid
                question="What is Kevin doing right now?",
                options=OPTIONS,
                is_anonymous=False,
                allows_multiple_answers=False
            )
            print(f"[{datetime.now()}] Poll sent to topic {TOPIC_1_ID}")
        except Exception as e:
            print(f"[{datetime.now()}] Failed to send poll to topic {TOPIC_1_ID}: {e}")
            print(f"[{datetime.now()}] Trying group chat without topic...")
            try:
                bot.send_poll(
                    chat_id=GROUP_ID,
                    question="What is Kevin doing right now?",
                    options=OPTIONS,
                    is_anonymous=False,
                    allows_multiple_answers=False
                )
                print(f"[{datetime.now()}] Poll sent to group chat instead")
            except Exception as e2:
                print(f"[{datetime.now()}] Failed to send poll to group: {e2}")
    else:
        print(f"[{datetime.now()}] Outside allowed hours, poll skipped")

def main():
    bot = Bot(token=BOT_TOKEN)
    print(f"[{datetime.now()}] Bot started, sending first poll immediately")
    
    send_poll(bot)  # first poll immediately
    
    while True:
        now = datetime.now()
        if not (START_HOUR <= now.hour < END_HOUR):
            next_time = next_allowed_time(now)
            wait_seconds = seconds_until(next_time)
            print(f"[{datetime.now()}] Sleeping until {next_time} ({wait_seconds:.0f}s)")
            time.sleep(wait_seconds)
            continue
        
        next_quarter = next_quarter_exact()
        wait_seconds = seconds_until(next_quarter)
        print(f"[{datetime.now()}] Waiting {wait_seconds:.0f}s until next poll at {next_quarter}")
        time.sleep(wait_seconds)
        send_poll(bot)

if __name__ == "__main__":
    main()