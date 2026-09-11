import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN
from ai.router import router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "🤖 <b>KASPER AI</b> на связи.\n"
        "Просто напиши мне что-нибудь — и я отвечу."
    )


@dp.message()
async def ai_handler(message: Message):
    if not message.text:
        return

    status = await message.answer("🧠 Думаю...")

    try:
        answer = await router.ask(message.text)
    except Exception:
        logging.exception("Ошибка AI")
        answer = "⚠️ Что-то пошло не так. Попробуй ещё раз."

    if len(answer) > 4000:
        answer = answer[:4000] + "..."

    await status.edit_text(answer, parse_mode="HTML")


# --- Мини-сайт-заглушка, чтобы Render видел "дверь" ---
async def health(request):
    return web.Response(text="KASPER AI is running")


async def start_web():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Health server on port {port}")


async def main():
    await start_web()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
