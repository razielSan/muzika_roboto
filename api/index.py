import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from fastapi import FastAPI, Request
from aiogram.types import Update

from app.bot.core.startup import setup_bot
from core.context.context import create_app_context
from core.context.runtime import ContextRuntime

app = FastAPI()

_bot = None
_dp = None
_inited = False


async def init():
    global _bot, _dp, _inited

    if _inited:
        return

    ctx = create_app_context()
    ContextRuntime.init(ctx)

    result = await setup_bot()

    if not result.ok:
        raise Exception(result.error.message)

    _, _dp, _bot = result.data

    _inited = True


@app.get("/")
async def root():
    return {"ok": True}


@app.get("/set-webhook")
async def set_webhook():
    await init()

    await _bot.set_webhook(
        url="https://muzika-roboto.vercel.app/webhook",
        drop_pending_updates=True
    )

    return {"ok": True}


@app.post("/webhook")
async def webhook(request: Request):
    await init()

    data = await request.json()
    update = Update.model_validate(data)

    await _dp.feed_webhook_update(_bot, update)

    return {"ok": True}