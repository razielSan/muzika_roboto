import sys

import aiohttp

from app.bot.core.startup import setup_bot
from app.bot.settings import settings
from app.bot.core.bot import telegram_bot
from core.logging.api import get_loggers
from core.error_handlers.format import format_errors_message


async def run_bot() -> None:
    """Подлючает все параметры для бота и запускает его."""
    # Встаем в try/except чтобы отловить все что не попало в middleware
    try:

        logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
        result_startup = await setup_bot()
        if not result_startup.ok:
            logging_data.critical_logger.critical(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=run_bot.__name__,
                    error_text=f"[STARTUP FAILED] {result_startup.error.code} {result_startup.error.message}",
                )
            )
            sys.exit()

        get_main_keyboards, dp = result_startup.data

        # Создаем глобальную сессию для всего бота. Будет доступ в роутерах через
        # название указанное ниже
        async with aiohttp.ClientSession() as session:
            dp["session"] = session
            dp["get_main_keyboards"] = get_main_keyboards
            logging_data.info_logger.info("bot запущен")
            await dp.start_polling(telegram_bot)

    except Exception:
        logging_data.info_logger.exception(
            f"Критическая ошибка при работа бота - {settings.SERVICE_NAME}"
        )
