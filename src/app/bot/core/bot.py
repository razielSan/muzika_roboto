from typing import Optional

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher

from app.bot.settings import ProxySettings, proxy_settings


def create_bot(
    bot_settings,
    logging_data,
    proxy: Optional[ProxySettings] = None,
):
    if proxy:
        proxy_source: str = (
            "WEBSHARE PROXY" if proxy_settings.USE_WEBSHARE_PROXY else "OTHER PROXY"
        )

        session: AiohttpSession = AiohttpSession(proxy=proxy)

        logging_data.info_logger.info(msg=f"[USE {proxy_source}] Прокси подключены")
        return Bot(token=bot_settings.TOKEN, session=session)

    logging_data.info_logger.info("[NOT USED PROXY] Прокси не были использованы")
    return Bot(token=bot_settings.TOKEN)


dp: Dispatcher = Dispatcher()
