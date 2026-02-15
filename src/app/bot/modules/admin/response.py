# Responses, strings, text for module admin
from pathlib import Path

from core.module_loader.runtime.loader import get_child_modules_settings_inline_data
from app.app_utils.keyboards import get_total_buttons_inline_kb
from app.bot.core.paths import bot_path
from core.logging.api import get_loggers
from .settings import settings


logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)



inline_data = get_child_modules_settings_inline_data(
    module_path=bot_path.BOT_DIR / "modules" / Path("admin/childes"),
    root_package="app.bot.modules.admin.childes",
    logging_data=logging_data,
)
if len(inline_data) >= 1:
    buttons_array = [button.text for button in inline_data]
    buttons = ", ".join(buttons_array)
    logging_data.info_logger.info(
        msg=f"[CREATE INLINE KEYBOARDS] Инлайн клавиатура для модуля {settings.SERVICE_NAME} создана\nКнопки - {buttons}"
    )

get_keyboards_menu_buttons = get_total_buttons_inline_kb(
    list_inline_kb_data=inline_data, quantity_button=1
)
