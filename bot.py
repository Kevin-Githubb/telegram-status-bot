import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ==============================
# CONFIG
# ==============================
# Replace this with your bot token string
TOKEN = os.environ.get("BOT_TOKEN")

# Global list to store dynamic options
options = ["Option 1", "Option 2"]  # starting default options


# ==============================
# BOT COMMAND HANDLERS
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm alive. Use /options to see current options."
    )


async def show_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if options:
        text = "\n".join(f"- {opt}" for opt in options)
        await update.message.reply_text(f"Current options:\n{text}")
    else:
        await update.message.reply_text("No options yet.")


async def add_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /add <option>")
        return
    new_option = " ".join(context.args)
    options.append(new_option)
    await update.message.reply_text(f"Added new option: {new_option}")


# ==============================
# SCHEDULER JOB
# ==============================
async def scheduled_job():
    # Example: print to console or do something with options
    print("Scheduled job running! Current options:", options)


# ==============================
# MAIN ASYNC FUNCTION
# ==============================
async def main():
    # Build bot application
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("options", show_options))
    app.add_handler(CommandHandler("add", add_option))

    # Setup scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_job, "interval", seconds=60)  # every 60 seconds
    scheduler.start()  # runs inside the bot's event loop

    # Start the bot (this will run forever until stopped)
    print("Bot starting...")
    await app.run_polling()


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    asyncio.run(main())