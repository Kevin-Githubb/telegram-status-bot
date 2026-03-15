import asyncio
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ======= CONFIG =======
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
USERS = {"@iteachbad": "Kevin", "@ilearnbad": "Giselle"}  # map usernames to names
OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]
CHAT_ID = "YOUR_CHAT_ID_HERE"  # can be a group or personal chat ID
RESET_INTERVAL_MINUTES = 15  # change later, initially can trigger immediately
# ====================

# State to track selections
user_selections = {}
waiting_for_free_text = None  # store username if "Others" pressed


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send options menu."""
    await send_options_menu(context)


async def send_options_menu(context: ContextTypes.DEFAULT_TYPE):
    """Send inline keyboard with options."""
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=opt)] for opt in OPTIONS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=CHAT_ID, text="Select your activity:", reply_markup=reply_markup
    )


async def option_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle option pressed by a user."""
    global waiting_for_free_text

    query = update.callback_query
    await query.answer()
    user = query.from_user.username
    selection = query.data

    # If user pressed "Others", wait for free text
    if selection == "Others":
        waiting_for_free_text = user
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"{USERS.get(user, user)}, please type your activity now.",
        )
        return

    # Record selection
    user_selections[user] = selection
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=f"{USERS.get(user, user)}: {selection}",
    )

    # Check if both users have selected
    if all(u in user_selections for u in USERS):
        await context.bot.send_message(chat_id=CHAT_ID, text="Both have selected! Options reset.")
        user_selections.clear()
        await send_options_menu(context)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free-text for 'Others' option."""
    global waiting_for_free_text
    user = update.message.from_user.username
    text = update.message.text

    if waiting_for_free_text == user:
        user_selections[user] = text
        await context.bot.send_message(
            chat_id=CHAT_ID, text=f"{USERS.get(user, user)}: {text}"
        )
        waiting_for_free_text = None

        # Check if both users have selected
        if all(u in user_selections for u in USERS):
            await context.bot.send_message(chat_id=CHAT_ID, text="Both have selected! Options reset.")
            user_selections.clear()
            await send_options_menu(context)


async def reset_options_periodically(context: ContextTypes.DEFAULT_TYPE):
    """Reset the options menu every quarter-hour."""
    while True:
        now = datetime.now()
        # Next quarter-hour
        next_minute = (now.minute // 15 + 1) * 15
        next_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=next_minute)
        wait_seconds = (next_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        user_selections.clear()
        await send_options_menu(context)


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # Inline button presses
    app.add_handler(CallbackQueryHandler(option_selected))

    # Free-text input for "Others"
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start periodic reset task
    app.create_task(reset_options_periodically(app))

    # For immediate testing on deploy, send options right away
    await send_options_menu(app)

    await app.run_polling()


if __name__ == "__main__":
    import nest_asyncio

    nest_asyncio.apply()  # ensures no "event loop already running" in some containers
    asyncio.run(main())