from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher
from app.bot.settings import ProxySettings


def create_bot(
    bot_settings,
    proxy_settings: ProxySettings,
    logging_data,
):
    proxy = proxy_settings.get_proxy_url()
    if proxy:

        session: AiohttpSession = AiohttpSession(proxy=proxy)

        logging_data.info_logger.info(msg="[USE PROXY] Прокси подключены")
        return Bot(token=bot_settings.TOKEN, session=session)

    logging_data.info_logger.info("[NOT USED PROXY] Прокси не были использованы")
    return Bot(token=bot_settings.TOKEN)


dp: Dispatcher = Dispatcher()
