from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher


def create_bot(bot_settings, proxy_settings, logging_data):

    if proxy_settings.USE_PROXY:
        session: AiohttpSession = AiohttpSession(proxy=proxy_settings.get_http_url())

        logging_data.info_logger.info(
            msg="[USE PROXY] Прокси подключены"
        )
        return Bot(token=bot_settings.TOKEN, session=session)

    logging_data.info_logger.info("[NOT USED PROXY] Прокси не были использованы")
    return Bot(token=bot_settings.TOKEN)


dp: Dispatcher = Dispatcher()
