import asyncio
from telegram import Poll
from telegram.ext import ApplicationBuilder, ContextTypes

# Your bot token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Chat/topic IDs
TOPIC_2_CHAT_ID = -1001234567890  # replace with your chat id

# Poll options
OPTIONS = ["Option 1", "Option 2", "Option 3"]

# Interval between polls (in seconds)
POLL_INTERVAL = 15 * 60  # 15 minutes


async def send_poll(app):
    """
    Sends a poll to the target chat and returns the poll message id.
    """
    message = await app.bot.send_poll(
        chat_id=TOPIC_2_CHAT_ID,
        question="Please choose an option:",
        options=OPTIONS,
        is_anonymous=False,
        allows_multiple_answers=False
    )
    return message.poll.id, message.message_id


async def poll_cycle(app):
    """
    Sends a poll once every POLL_INTERVAL seconds.
    """
    while True:
        try:
            poll_id, msg_id = await send_poll(app)
            print(f"Poll sent! Poll ID: {poll_id}, Message ID: {msg_id}")
        except Exception as e:
            print(f"Error sending poll: {e}")
        await asyncio.sleep(POLL_INTERVAL)


async def start_poll_loop(application):
    """
    PTB post_init function to start the polling loop.
    """
    asyncio.create_task(poll_cycle(application))


def main():
    # Create the application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Assign the post_init to start the poll loop
    app.post_init = start_poll_loop

    # Run the bot (blocking)
    print("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()