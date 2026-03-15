import asyncio
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

# --- CONFIG ---
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
USERS = {
    "@iteachbad": "Kevin",
    "@ilearnbad": "Giselle"
}
OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]
RESET_INTERVAL_MINUTES = 15  # every quarter hour

# --- GLOBAL STATE ---
user_selections = {}  # {username: option or text}
current_message_id = None
chat_id = None

# --- FUNCTIONS ---

def get_keyboard():
    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in OPTIONS]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_id
    chat_id = update.effective_chat.id
    await send_options(context)

async def send_options(context: ContextTypes.DEFAULT_TYPE):
    global current_message_id
    user_selections.clear()
    if chat_id:
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text="Choose an activity:",
            reply_markup=get_keyboard()
        )
        current_message_id = msg.message_id

async def handle_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    username = f"@{query.from_user.username}"
    user_display = USERS.get(username)
    if not user_display:
        await query.answer("You are not registered for this bot.")
        return

    await query.answer()  # acknowledge callback

    # Check for 'Others' selection
    if query.data == "Others":
        await query.message.reply_text(f"{username}, please type your custom activity:")
        # Mark waiting for text
        user_selections[username] = None
    else:
        user_selections[username] = query.data

    # If both users have responded, post messages
    if all(u in user_selections and user_selections[u] for u in USERS):
        for u, name in USERS.items():
            await context.bot.send_message(chat_id=chat_id, text=f"{name}: {user_selections[u]}")
        # Delete the options message
        if current_message_id:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=current_message_id)
            except:
                pass
        user_selections.clear()  # ready for next round

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = f"@{update.message.from_user.username}"
    if username not in USERS:
        return
    # Only accept if user had selected 'Others' and waiting for input
    if username in user_selections and user_selections[username] is None:
        user_selections[username] = update.message.text

        # Check if both users are done
        if all(u in user_selections and user_selections[u] for u in USERS):
            for u, name in USERS.items():
                await context.bot.send_message(chat_id=chat_id, text=f"{name}: {user_selections[u]}")
            # Delete the options message
            if current_message_id:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=current_message_id)
                except:
                    pass
            user_selections.clear()

async def reset_options_periodically(application):
    # Immediate trigger for testing
    await asyncio.sleep(1)
    if chat_id:
        await send_options(application)
    # Schedule every quarter hour
    while True:
        now = datetime.now()
        next_run = (now + timedelta(minutes=RESET_INTERVAL_MINUTES)).replace(second=0, microsecond=0)
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        if chat_id:
            await send_options(application)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_option))
    app.add_handler(CommandHandler("reset", lambda u, c: send_options(c)))  # optional manual reset
    app.add_handler(app.message_handler(handle_text, filters=None))  # handle free text

    # Start the periodic reset task
    app.create_task(reset_options_periodically(app))

    print("Bot starting...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())