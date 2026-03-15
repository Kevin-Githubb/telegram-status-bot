import os
import asyncio
from telegram import Bot, Update, Poll, PollOption
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters, PollHandler

# Environment bot token
TOKEN = os.environ.get("BOT_TOKEN")

# Group & Topics
GROUP_ID = -1003893865263
TOPIC_1_ID = 190  # Messages with user activity
TOPIC_2_ID = 191  # Poll options

# Users mapping
USER_MAP = {
    "@iteachbad": "Kevin",
    "@ilearnbad": "Giselle"
}

# Poll options
OPTIONS = ["Eating", "Studying", "Working", "Traveling", "Others"]

# Track responses per poll
poll_data = {}

async def send_poll(app: ApplicationBuilder):
    """Send poll to topic 2 and store poll_id"""
    message = await app.bot.send_poll(
        chat_id=GROUP_ID,
        question="Choose your current activity:",
        options=OPTIONS,
        type=Poll.REGULAR,
        is_anonymous=False,
        allow_multiple_answers=False,
        message_thread_id=TOPIC_2_ID
    )
    poll_id = message.poll.id
    poll_data[poll_id] = {}  # store user responses
    print(f"Poll sent with id {poll_id}")
    return poll_id, message.message_id

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle poll answer updates"""
    poll_id = update.poll_answer.poll_id
    user_name = update.poll_answer.user.username
    option_ids = update.poll_answer.option_ids

    if poll_id not in poll_data:
        return  # ignore old polls

    # Map user to their chosen option text
    if user_name in USER_MAP:
        choice_text = OPTIONS[option_ids[0]] if option_ids else "No selection"
        poll_data[poll_id][user_name] = choice_text
        print(f"{USER_MAP[user_name]} selected {choice_text}")

    # Check if both users have responded
    if all(u in poll_data[poll_id] for u in USER_MAP):
        # Send messages to topic 1
        for uname, display_name in USER_MAP.items():
            text = f"{display_name}: {poll_data[poll_id][uname]}"
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=text,
                message_thread_id=TOPIC_1_ID
            )
        # Delete the poll message from topic 2
        await context.bot.delete_message(
            chat_id=GROUP_ID,
            message_id=poll_data[poll_id]["message_id"],
            message_thread_id=TOPIC_2_ID
        )
        # Clean up
        del poll_data[poll_id]

async def poll_cycle(app: ApplicationBuilder):
    """Send poll every quarter-hour"""
    while True:
        poll_id, msg_id = await send_poll(app)
        # Store message_id for deletion
        poll_data[poll_id]["message_id"] = msg_id

        # Wait 15 minutes before next poll
        await asyncio.sleep(900)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(PollHandler(handle_poll_answer))

    # Start poll cycle task
    asyncio.create_task(poll_cycle(app))

    # Start bot
    print("Bot starting...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())