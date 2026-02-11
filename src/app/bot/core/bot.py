from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher

from core.logging.api import get_loggers


def create_bot(bot_settings, proxy_settings):
    logging_data = get_loggers(name=bot_settings.NAME_FOR_LOG_FOLDER)

    if proxy_settings.USE_PROXY:
        session: AiohttpSession = AiohttpSession(proxy=proxy_settings.get_http_url())

        logging_data.info_logger.info(msg="Бот запущен с использванием прокси")
        return Bot(token=bot_settings.TOKEN, session=session)

    logging_data.info_logger.info("Бот запущен в обычном режиме")
    return Bot(token=bot_settings.TOKEN)


dp: Dispatcher = Dispatcher()
