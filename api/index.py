from fastapi import FastAPI, Request

from app.bot.core.startup import setup_bot
from aiogram.types import Update

app = FastAPI()

_bot = None
_dp = None
_inited = False


async def init():
    global _bot, _dp, _inited

    if _inited:
        return

    result = await setup_bot()
    _, _dp, _bot = result.data

    await _bot.set_webhook(
        url="https://YOUR-PROJECT.vercel.app/webhook"
    )

    _inited = True


@app.post("/webhook")
async def webhook(request: Request):
    await init()

    data = await request.json()

    update = Update.model_validate(data)

    await _dp.feed_webhook_update(_bot, update)

    return {"ok": True}