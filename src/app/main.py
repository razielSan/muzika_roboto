import asyncio
import signal
import sys

from core.logging.api import get_loggers
from app.settings import settings as app_settings
from app.bot.main import run_bot
from core.context.context import create_app_context
from core.context.runtime import ContextRuntime


# Меняет тип event_loop для виндоус чтобы при нажатии ctl+c не было ошибки KeyboardInterrupt
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main() -> None:
    """Синхронная точка входа для console_scripts."""
    try:
        try:
            ctx = create_app_context()
            ContextRuntime.init(ctx)
        except Exception as err:
            print("FATAL: Ошибка при создание логов")
            print(err)
            sys.exit()

        logging_data = get_loggers(name=app_settings.NAME_FOR_LOG_FOLDER)
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logging_data.info_logger.info("Приложение остановлено вручную (Ctrl+C)")
    except Exception:
        logging_data.error_logger.error("Критическая ошибка в async приложении")
        raise


async def async_main() -> None:
    """Async логика приложения."""
    if sys.platform == "win32":
        await _run_windows()
    else:
        await _run_unix()


async def _run_unix():
    """Запуск приложения на unix-системе."""

    logging_data = get_loggers(name=app_settings.NAME_FOR_LOG_FOLDER)

    # корректно завершает работу на сервере
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    logging_data.info_logger.info("Приложение запущен(Unix mode)")
    await asyncio.gather(run_bot(), stop_event.wait())


async def _run_windows():
    """Запуск приложения на windows."""

    logging_data = get_loggers(name=app_settings.NAME_FOR_LOG_FOLDER)
    try:
        # Запускам бота
        logging_data.info_logger.info("Приложение запущено (Windows mode)")
        await run_bot()
    except Exception:
        logging_data.error_logger.exception(
            "Необработанное исключение при запуске Windows"
        )
        raise
    finally:
        logging_data.info_logger.info("Приложение завершило работу корректно")
