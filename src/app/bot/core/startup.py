from pathlib import Path
from typing import List
import traceback

from app.bot.core.bot import dp
from app.bot.core.paths import bot_path
from app.bot.core.bot import create_bot
from app.bot.settings import settings, proxy_settings
from app.bot.core.middleware.errors import RouterErrorMiddleware
from core.module_loader.runtime.loader import load_modules
from core.utils.filesistem import ensure_directories
from core.module_loader.runtime.register import register_module
from core.logging.api import get_loggers
from core.contracts.constants import (
    DEFAULT_BOT_MODULES_ROOT,
    DEFAULT_NAME_ROUTER,
    DEFAULT_NAME_SETTINGS,
)
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result, InlineKeyboardData
from core.error_handlers.format import format_errors_message
from app.app_utils.keyboards import get_total_buttons_inline_kb


async def setup_bot() -> Result:
    """Подключает все необходимые компоненты для работы бота."""
    try:

        logging_bot = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

        if not settings.DB_PATH.exists():
            raise RuntimeError("Database not initialized. Please contact developer.")

        result_load_modules = load_modules(
            root_package=DEFAULT_BOT_MODULES_ROOT,
            name_router=DEFAULT_NAME_ROUTER,
            name_settings=DEFAULT_NAME_SETTINGS,
        )
        if not result_load_modules.ok:
            return result_load_modules

        array_modules = result_load_modules.data

        register_module(
            dp=dp,
            modules=array_modules,
            logging_data=logging_bot,
            name=DEFAULT_NAME_ROUTER,
        )  # регестрируем модули

        settings_array_modules = [
            getattr(model.settings, DEFAULT_NAME_SETTINGS) for model in array_modules
        ]
        list_path_to_temp_folder = [
            bot_path.TEMP_DIR / Path(config.NAME_FOR_TEMP_FOLDER)
            for config in settings_array_modules
        ]  # получаем список из путей для папки temp

        result_directory = ensure_directories(
            bot_path.TEMP_DIR,
            bot_path.STATIC_DIR,
            *list_path_to_temp_folder,
            logging_data=logging_bot,
        )  # создает нужные пути
        if not result_directory.ok:
            return result_directory

        root_modules = [m for m in array_modules if m.is_root]

        settings_root_modules = [
            getattr(module.settings, DEFAULT_NAME_SETTINGS) for module in root_modules
        ]

        # Формируем инлайн клавиатуру для главного меню
        inline_data = [
            InlineKeyboardData(
                text=config.MENU_CALLBACK_TEXT,
                callback_data=config.MENU_CALLBACK_DATA,
            )
            for config in settings_root_modules
            if config.SHOW_IN_MAIN_MENU
        ]
        if len(inline_data) == 0:
            logging_bot.warning_logger.warning(
                "Инлайн клавиатура для "
                "главного меню не была создана:\nПодключен только главный модуль"
                " или остальные модули скрыты"
            )
        else:
            buttons_array = [button.text for button in inline_data]
            buttons = ", ".join(buttons_array)
            logging_bot.info_logger.info(
                msg=f"[CREATE INLINE KEYBOARDS] Инлайн клавиатура для модуля main создана\nКнопки - {buttons}"
            )

        get_main_inline_keyboards = get_total_buttons_inline_kb(
            list_inline_kb_data=inline_data, quantity_button=2
        )

        for model in root_modules:
            # получаем  логгеры

            config = getattr(model.settings, DEFAULT_NAME_SETTINGS)
            router = getattr(model.router, DEFAULT_NAME_ROUTER)

            logging_data = get_loggers(
                name=config.NAME_FOR_LOG_FOLDER,
            )

            # Подключаем middleware
            router.message.middleware(
                RouterErrorMiddleware(
                    logger=logging_data.error_logger,
                )
            )
            router.callback_query.middleware(
                RouterErrorMiddleware(logger=logging_data.error_logger)
            )

            logging_bot.info_logger.info(
                f"Middleware для {logging_data.router_name} подключен"
            )

        telegram_bot = create_bot(
            bot_settings=settings,
            proxy_settings=proxy_settings,
        )

        await telegram_bot.set_my_commands(
            commands=settings.LIST_BOT_COMMANDS  # Добавляет команды боту
        )  # Добавляет команды боту
        await telegram_bot.delete_webhook(
            drop_pending_updates=True
        )  # Игнорирует все присланные сообщение пока бот не работал

        return ok(data=(get_main_inline_keyboards, dp, telegram_bot))
    except Exception as err:
        logging_bot.error_logger.error(
            msg=format_errors_message(
                name_router=logging_bot.router_name,
                function_name=setup_bot.__name__,
                error_text=f"Критическая ошибка в работе startup\n{traceback.format_exc()}",
            )
        )
        return fail(
            code="STARTUP FAIL",
            message=f"Критическая ошибка в работе startup - {err}",
            details=str(traceback.format_exc()),
        )
