import logging

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .bot_handlers import (
    add_handler,
    bets_handler,
    help_handler,
    history_handler,
    start_handler,
    stats_handler,
    text_message_handler,
)
from .settings import load_settings, validate_settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def debug_update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.effective_message

    print("\n=== UPDATE RECEIVED ===")
    print("user_id:", user.id if user else None)
    print("username:", user.username if user else None)
    print("text:", message.text if message else None)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("\n=== BOT ERROR ===")
    print(context.error)


def run_bot() -> None:
    settings = load_settings()
    validate_settings(settings)

    print("=== BOT STARTING ===")
    print("allowed_user_id:", settings.allowed_user_id)
    print("allowed_username:", settings.allowed_username)

    application: Application = ApplicationBuilder().token(settings.bot_token).build()
    application.bot_data["settings"] = settings

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("stats", stats_handler))
    application.add_handler(CommandHandler("history", history_handler))
    application.add_handler(CommandHandler("bets", bets_handler))
    application.add_handler(CommandHandler("add", add_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)
    )

    application.add_handler(MessageHandler(filters.ALL, debug_update_handler), group=999)
    application.add_error_handler(error_handler)

    print("=== BOT STARTED. WAITING FOR UPDATES ===")
    application.run_polling()


if __name__ == "__main__":
    run_bot()
