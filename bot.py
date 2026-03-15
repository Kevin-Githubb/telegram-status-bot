import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# ===== CONFIG =====
TOKEN = os.environ.get("BOT_TOKEN")

# ===== OPTIONS =====
OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]

# ===== STATES =====
WAITING_FOR_MANUAL_TEXT = 1

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[opt] for opt in OPTIONS]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Choose what Kevin is doing:", reply_markup=reply_markup)
    return WAITING_FOR_MANUAL_TEXT

async def option_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice != "Others":
        await update.message.reply_text(f'Kevin: "{choice}"', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please type your custom activity for Kevin:", reply_markup=ReplyKeyboardRemove())
        return WAITING_FOR_MANUAL_TEXT

async def manual_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f'Kevin: "{text}"')
    return ConversationHandler.END

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
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manual_text))

    print("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()