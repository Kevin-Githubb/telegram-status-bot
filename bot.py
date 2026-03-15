import asyncio
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta

# ---------------- CONFIG ----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = -1003893865263  # Supergroup chat
TOPIC1_ID = 190  # Activity messages
TOPIC2_ID = 191  # Polling options

USERS = {
    "@iteachbad": "Kevin",
    "@ilearnbad": "Giselle"
}

OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]

# State tracking
current_poll = {}
selected_users = set()

# ---------------- HELPERS ----------------
def build_keyboard():
    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in OPTIONS]
    return InlineKeyboardMarkup(keyboard)

async def send_poll(app):
    """Send poll in Topic 2."""
    global current_poll, selected_users
    current_poll = {}
    selected_users.clear()
    await app.bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=TOPIC2_ID,
        text="Choose your activity:",
        reply_markup=build_keyboard()
    )

def next_quarter():
    """Return datetime of next quarter hour."""
    now = datetime.now()
    minute = (now.minute // 15 + 1) * 15
    hour = now.hour
    if minute == 60:
        minute = 0
        hour += 1
    return now.replace(hour=hour % 24, minute=minute, second=0, microsecond=0)

# ---------------- HANDLERS ----------------
async def handle_poll_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    global current_poll, selected_users
    query = update.callback_query
    await query.answer()
    username = query.from_user.username
    choice = query.data

    if username not in USERS:
        await query.edit_message_text("You are not authorized to select.")
        return

    # Save selection
    current_poll[username] = choice
    selected_users.add(username)

    # If 'Others', ask for manual input
    if choice == "Others":
        await context.bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=TOPIC2_ID,
            text=f"{USERS[username]}, please type your activity."
        )

    # If both selected, post in Topic 1 and delete buttons
    if len(selected_users) == 2:
        for user, act in current_poll.items():
            # Skip if still 'Others' waiting for text
            if act == "Others":
                continue
            await context.bot.send_message(
                chat_id=CHAT_ID,
                message_thread_id=TOPIC1_ID,
                text=f"{USERS[user]}: {act}"
            )
        # Clear poll
        await query.edit_message_text("Poll closed. Next poll in 15 minutes.")
        current_poll.clear()
        selected_users.clear()

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manual text for 'Others' option."""
    global current_poll
    username = update.message.from_user.username
    if username not in current_poll or current_poll[username] != "Others":
        return

    text = update.message.text
    await context.bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=TOPIC1_ID,
        text=f"{USERS[username]}: {text}"
    )
    # Mark as selected
    selected_users.add(username)

    if len(selected_users) == 2:
        # Delete poll message (optional, leave text as record)
        await context.bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=TOPIC2_ID,
            text="Poll closed. Next poll in 15 minutes."
        )
        current_poll.clear()
        selected_users.clear()

# ---------------- SCHEDULER ----------------
async def reset_options_periodically(app):
    """Trigger poll every quarter hour."""
    while True:
        await send_poll(app)
        now = datetime.now()
        next_run = next_quarter()
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)

# ---------------- MAIN ----------------
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CallbackQueryHandler(handle_poll_selection))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Immediate poll for testing
    await send_poll(app)

    # Start periodic polling
    app.create_task(reset_options_periodically(app))

    print("Bot starting...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())