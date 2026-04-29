import json
from aiogram.types import Update

from app.bot.core.startup import setup_bot
from app.bot.settings import settings

_bot = None
_dp = None
_initialized = False


async def init():
    global _bot, _dp, _initialized

    if _initialized:
        return

    result = await setup_bot()
    _, _dp, _bot = result.data

    await _bot.set_webhook(
        url=settings.WEBHOOK_URL,
        drop_pending_updates=True,
    )

    _initialized = True


async def handler(request):
    await init()

    body = request.body
    if isinstance(body, bytes):
        body = body.decode()

    data = json.loads(body)

    update = Update.model_validate(data)

    await _dp.feed_webhook_update(
        bot=_bot,
        update=update,
    )

    return {"statusCode": 200, "body": "ok"}
