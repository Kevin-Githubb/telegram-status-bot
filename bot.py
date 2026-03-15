import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ====== CONFIG ======
TOKEN = os.environ.get("BOT_TOKEN")  # Token from environment variable

# Example dynamic options list
options = ["Option 1", "Option 2", "Option 3"]

# ====== COMMAND HANDLERS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is running.")

async def show_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Here are the current options:\n" + "\n".join(f"- {opt}" for opt in options)
    await update.message.reply_text(text)

async def add_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /add_option Your new option
    if context.args:
        new_option = " ".join(context.args)
        options.append(new_option)
        await update.message.reply_text(f"Added option: {new_option}")
    else:
        await update.message.reply_text("Usage: /add_option <your option>")

# ====== ASYNC SCHEDULER ======
async def periodic_task():
    while True:
        print("Scheduler task running...")
        # Example: could send message to a chat or do other async tasks
        await asyncio.sleep(60)  # Runs every 60 seconds

# ====== MAIN ======
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("show_options", show_options))
    app.add_handler(CommandHandler("add_option", add_option))

    # Start the scheduler as a background task
    app.create_task(periodic_task())

    print("Bot starting...")
    # Start polling (async loop handled internally)
    app.run_polling()

if __name__ == "__main__":
    main()