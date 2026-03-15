import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

# ===== CONFIG =====
TOKEN = "YOUR_BOT_TOKEN_HERE"

# ===== OPTIONS =====
OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]
WAITING_FOR_MANUAL_TEXT = 1

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[option] for option in OPTIONS]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Hi! Choose an activity for Kevin:", reply_markup=reply_markup)
    return WAITING_FOR_MANUAL_TEXT

# ===== HANDLE CHOICE =====
async def option_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice in OPTIONS and choice != "Others":
        await update.message.reply_text(f'Kevin: "{choice}"', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif choice == "Others":
        await update.message.reply_text("Please type your custom activity for Kevin:", reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_MANUAL_TEXT
    else:
        await update.message.reply_text("Please choose a valid option.")
        return WAITING_FOR_MANUAL_TEXT

# ===== HANDLE MANUAL TEXT =====
async def manual_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f'Kevin: "{text}"')
    return ConversationHandler.END

# ===== CANCEL =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_MANUAL_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, option_chosen),
                MessageHandler(filters.TEXT & ~filters.COMMAND, manual_text),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()