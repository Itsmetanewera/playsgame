# bot.py (коротко)
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Message
from aiogram.filters import Command

BOT_TOKEN = os.getenv("8521116610:AAE_aPCZ7KpXS2VPnPEtgYrHJ2oNMbNzJ70")  # на Railway задаём секрет
ADMIN_IDS = {int(x) for x in os.getenv("6591391434").split(",") if x.strip().isdigit()}
WEBAPP_URL = os.getenv("WEBAPP_URL","https://plays.io")  # указать plays.io

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
from aiogram import Router
router = Router()
dp.include_router(router)

@router.message(Command("start"))
async def start(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [ InlineKeyboardButton(text="Open Plays MiniApp", web_app=WebAppInfo(url=WEBAPP_URL)) ]
    ])
    await m.answer("Открыть мини-приложение:", reply_markup=kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
