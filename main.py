import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dotenv import load_dotenv
import uvicorn

load_dotenv()

BOT_TOKEN = os.getenv("8521116610:AAE_aPCZ7KpXS2VPnPEtgYrHJ2oNMbNzJ70")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
DOMAIN = os.getenv("plays.io")
PORT = int(os.getenv("PORT", 8000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    # Удаляем старый webhook
    await bot.delete_webhook(drop_pending_updates=True)

    # Устанавливаем новый webhook
    await bot.set_webhook(url=DOMAIN + WEBHOOK_PATH)
    print("Webhook установлен:", DOMAIN + WEBHOOK_PATH)


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}


@app.get("/")
def home():
    return {"status": "running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)

