"""FaceVault KYC bot using aiogram v3 (async).

Install:
    pip install facevault aiogram

Usage:
    BOT_TOKEN=... FACEVAULT_API_KEY=fv_live_... python aiogram_v3.py

User flow:
    1. User sends /verify
    2. Bot creates FaceVault session and shows inline Mini App button
    3. User completes KYC in the Mini App
    4. Webhook delivers result (aiogram v3 inline keyboard mode)
"""

import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from facevault import AsyncFaceVaultClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
FACEVAULT_API_KEY = os.environ["FACEVAULT_API_KEY"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

fv = AsyncFaceVaultClient(api_key=FACEVAULT_API_KEY)


@dp.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer("Welcome! Use /verify to start identity verification.")


@dp.message(Command("verify"))
async def verify(message: Message) -> None:
    """Create a FaceVault session and show the Mini App button."""
    user_id = str(message.from_user.id)
    session = await fv.create_session(external_user_id=user_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Verify Identity",
            web_app=WebAppInfo(url=session.webapp_url),
        )
    ]])

    await message.answer(
        "Tap the button below to verify your identity:",
        reply_markup=keyboard,
    )


@dp.message(Command("check"))
async def check(message: Message) -> None:
    """Poll the most recent session (simplified — in production, store session_id)."""
    await message.answer(
        "Use webhooks to receive results automatically.\n"
        "See the FaceVault docs for webhook setup."
    )


async def main() -> None:
    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
