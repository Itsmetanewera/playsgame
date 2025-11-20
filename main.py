import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def handle_message(message: types.Message):
    await message.answer(f"Привет! Ты написал: {message.text}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
