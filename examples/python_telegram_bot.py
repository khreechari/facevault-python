"""FaceVault KYC bot using python-telegram-bot v20+.

Install:
    pip install facevault python-telegram-bot

Usage:
    BOT_TOKEN=... FACEVAULT_API_KEY=fv_live_... python python_telegram_bot.py

User flow:
    1. User sends /verify
    2. Bot creates FaceVault session and shows Mini App button
    3. User completes KYC in the Mini App
    4. Bot receives result via web_app_data (reply keyboard) or webhook
"""

import json
import logging
import os

from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from facevault import FaceVaultClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
FACEVAULT_API_KEY = os.environ["FACEVAULT_API_KEY"]

fv = FaceVaultClient(api_key=FACEVAULT_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Use /verify to start identity verification."
    )


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a FaceVault session and show the Mini App button."""
    user_id = str(update.effective_user.id)
    session = fv.create_session(external_user_id=user_id)

    # Store session_id for later lookup
    context.user_data["session_id"] = session.session_id

    # Reply keyboard with web_app button — triggers sendData on completion
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("Verify Identity", web_app=WebAppInfo(url=session.webapp_url))]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(
        "Tap the button below to verify your identity:",
        reply_markup=keyboard,
    )


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle sendData() result from the Mini App."""
    data = json.loads(update.effective_message.web_app_data.data)
    status = data.get("status", "unknown")
    session_id = data.get("session_id")

    if status == "passed":
        await update.message.reply_text(
            f"Identity verified! Session: {session_id}",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif status == "failed":
        await update.message.reply_text(
            "Verification failed. Use /verify to try again.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            f"Verification ended with status: {status}",
            reply_markup=ReplyKeyboardRemove(),
        )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Poll session status (alternative to webhook/sendData)."""
    session_id = context.user_data.get("session_id")
    if not session_id:
        await update.message.reply_text("No active session. Use /verify first.")
        return

    status = fv.get_session(session_id)
    await update.message.reply_text(
        f"Session: {status.session_id}\n"
        f"Status: {status.status}\n"
        f"Face match: {status.face_match_passed}"
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    logger.info("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
