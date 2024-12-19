import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Activation Key
ACTIVATION_KEY = "ACTIVATION_KEY_93Fz8H2lM7JvY6wQdZpB5RkX0tVr4J1UqGzC8WkLz9T5OPXa47YmN2QW3R8KL9Zv5JtMX6CqN0RwP7BZLY834JXZPQWMNTR6VK1209"

# User activation status, expiration, and messages
user_status = {}
expiration_times = {}
user_messages = {}

# Generate Token Command
async def generate_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activation_link = "https://tpi.li/activationbot"
    message = await update.message.reply_text(
        f"🔑 Click this link to get the activation key: {activation_link}",
        disable_web_page_preview=True
    )
    user_messages.setdefault(update.effective_user.id, []).append(message.message_id)
    await asyncio.sleep(2)
    message = await update.message.reply_text(
        "✅ After getting the key, send it here to activate your token."
    )
    user_messages[update.effective_user.id].append(message.message_id)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args  # Retrieve the arguments passed via the /start command
    user_id = update.effective_user.id
    if args and args[0] == ACTIVATION_KEY:
        user_status[user_id] = True
        expiration_times[user_id] = datetime.now() + timedelta(hours=2)
        await update.message.reply_text(
            "✅ Activation successful! Use /access_video to watch exclusive study material.\n"
            "⚠️ Note: Your token will expire in 2 hours."
        )
        # Schedule chat cleanup
        asyncio.create_task(clean_chat_after_expiry(context, user_id))
    else:
        await update.message.reply_text(
            "👋 Welcome to Pinky Ponky Bot!\n"
            "This bot provides exclusive study material.\n"
            "To generate a token, click here - https://tpi.li/activationbot"
        )

# Check Token Status Command
async def check_token_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_time = datetime.now()

    if user_status.get(user_id, False):
        if current_time < expiration_times[user_id]:
            await update.message.reply_text(
                "✅ Your token is activated! Use /access_video to watch exclusive study material."
            )
        else:
            user_status[user_id] = False
            await update.message.reply_text(
                "❌ Your token has expired. Please activate it again.\n"
                "Generate token id from here - https://tpi.li/activationbot",
                disable_web_page_preview=True
            )
    else:
        await update.message.reply_text(
            "❌ Your token is not active.\n"
            "Please get the activation key and send it here.\n"
            "Generate token id from here - https://tpi.li/activationbot",
            disable_web_page_preview=True
        )

# Handle Activation Key
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text.strip()
    message = update.message

    if user_message == ACTIVATION_KEY:
        user_status[user_id] = True
        expiration_times[user_id] = datetime.now() + timedelta(hours=2)
        await message.reply_text(
            "✅ Activation successful! Use /access_video to watch exclusive study material.\n"
            "⚠️ Note: Your token will expire in 2 hours."
        )
        asyncio.create_task(clean_chat_after_expiry(context, user_id))
    else:
        await message.reply_text(
            "❌ Invalid activation key or message. Please try again by following the instructions."
        )
    user_messages.setdefault(user_id, []).append(message.message_id)

# Access Video Command
async def access_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_time = datetime.now()

    if user_status.get(user_id, False):
        if current_time < expiration_times[user_id]:
            video_url = "https://www.youtube.com/watch?v=rhi2CbFOYN4&list=RDrhi2CbFOYN4&start_radio=1"
            message = await update.message.reply_text(
                f"🎥 Here is your exclusive content: {video_url}\n"
                "⚠️ This message will be deleted after 30 minutes.",
                disable_web_page_preview=True
            )
            user_messages.setdefault(user_id, []).append(message.message_id)
            await asyncio.sleep(1800)
            try:
                await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
            except Exception as e:
                print(f"Failed to delete message: {e}")
        else:
            user_status[user_id] = False
            await update.message.reply_text(
                "❌ Your token has expired. Please activate it again.\n"
                "Generate token id from here - https://tpi.li/activationbot",
                disable_web_page_preview=True
            )
    else:
        await update.message.reply_text(
            "❌ You must activate your token first! Use the activation link to get the key.\n"
            "Generate token id from here - https://tpi.li/activationbot",
            disable_web_page_preview=True
        )

# Clean Chat After Expiry
async def clean_chat_after_expiry(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    await asyncio.sleep(7200)  # Wait for 2 hours
    if user_id in user_messages:
        for message_id in user_messages[user_id]:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=message_id)
            except Exception as e:
                print(f"Failed to delete message: {e}")
        del user_messages[user_id]

# Main Function
def main():
    app = ApplicationBuilder().token("7229864184:AAGrXVl2ITIZY9A5DHVoJGZwQtgS8_BpcJU").build()

    app.add_handler(CommandHandler("generate_token", generate_token))
    app.add_handler(CommandHandler("check_token_status", check_token_status))
    app.add_handler(CommandHandler("access_video", access_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Activation Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()


