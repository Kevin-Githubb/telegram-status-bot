import os
import time
from datetime import datetime, timedelta
from telegram import Bot

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
    minutes = ((now.minute // 15) + 1) * 15
    hour = now.hour
    if minutes == 60:
        minutes = 0
        hour += 1
    next_quarter = now.replace(hour=hour, minute=minutes, second=0, microsecond=0)
    
    # If outside allowed hours, move to next day's START_HOUR
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

def send_poll(bot: Bot):
    now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        try:
            message = bot.send_poll(
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
    else:
        print(f"[{datetime.now()}] Outside allowed hours. Poll skipped.")

# ------------------ Main ------------------

def main():
    bot = Bot(token=BOT_TOKEN)
    print(f"[{datetime.now()}] Bot started... Sending first poll immediately.")
    
    # --- Send first poll immediately ---
    send_poll(bot)
    
    while True:
        # Calculate seconds until the next exact quarter
        wait_seconds = seconds_until_next_quarter()
        print(f"[{datetime.now()}] Waiting {wait_seconds:.0f}s until next poll...")
        time.sleep(wait_seconds)
        send_poll(bot)

if __name__ == "__main__":
    main()