import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ==============================
# Configuration
# ==============================
TOKEN = "YOUR_BOT_TOKEN_HERE"  # <-- put your bot token here
USER_MAP = {
    "@iteachbad": "Kevin",
    "@ilearnbad": "Giselle"
}
OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]

# ==============================
# State
# ==============================
responses = {}  # username -> selected option / manual text
awaiting_manual = {}  # username -> True if waiting for "Others" input

# ==============================
# Helpers
# ==============================
def build_keyboard():
    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in OPTIONS]
    return InlineKeyboardMarkup(keyboard)

async def reset_options_periodically():
    while True:
        now = datetime.now()
        # Calculate next quarter hour
        minute = (now.minute // 15 + 1) * 15
        if minute == 60:
            next_reset = now.replace(hour=now.hour+1, minute=0, second=0, microsecond=0)
        else:
            next_reset = now.replace(minute=minute, second=0, microsecond=0)
        wait_seconds = (next_reset - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        responses.clear()
        awaiting_manual.clear()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Options reset for next round.")

# ==============================
# Command Handlers
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Select an activity:", 
        reply_markup=build_keyboard()
    )

# ==============================
# Callback Handler for Buttons
# ==============================
async def option_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    username = f"@{query.from_user.username}"
    option = query.data

    # If selecting "Others", wait for manual input
    if option == "Others":
        awaiting_manual[username] = True
        await query.message.reply_text(f"{USER_MAP[username]} selected 'Others'. Please type your activity manually.")
        return

    # Regular option
    responses[username] = option
    await query.message.reply_text(f"{USER_MAP[username]} selected {option}.")

    await check_and_post_results(context)

# ==============================
# Handle manual text input
# ==============================
async def manual_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = f"@{update.message.from_user.username}"
    if username in awaiting_manual:
        responses[username] = update.message.text
        awaiting_manual.pop(username)
        await update.message.reply_text(f"{USER_MAP[username]}: {update.message.text}")
        await check_and_post_results(context)

# ==============================
# Check if both users have responded
# ==============================
async def check_and_post_results(context: ContextTypes.DEFAULT_TYPE):
    if all(user in responses for user in USER_MAP.keys()):
        result_text = "\n".join(f"{USER_MAP[user]}: {responses[user]}" for user in USER_MAP.keys())
        await context.bot.send_message(chat_id=context.job.chat_id if hasattr(context.job, "chat_id") else context.application.bot.id, text=result_text)
        responses.clear()
        awaiting_manual.clear()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Posted results:\n{result_text}")

# ==============================
# Main
# ==============================
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(option_selected))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), manual_input))

    # Start periodic reset task
    app.create_task(reset_options_periodically())

    print("Bot starting...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())