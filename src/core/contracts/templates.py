from typing import Dict, List
from core.contracts.constants import (
    DEFAULT_NAME_OF_THE_ROUTER_FOLDER,
    DEFAULT_CHILD_SEPARATOR,
    DEFAULT_NAME_SETTINGS,
    DEFAULT_NAME_ROUTER,
)


TEMPLATE_FILES: Dict[str, str] = {
    """__init__.py""": "# init for {name}\n",
    f"{DEFAULT_NAME_ROUTER}.py": """from pathlib import Path
from importlib import import_module
from core.logging.api import get_loggers
from .settings import settings

from aiogram import Router
        
    
router: Router = Router(name=settings.SERVICE_NAME)

            
# Include sub router            
current_dir = Path(__file__).resolve().parent
handlers_path = current_dir / "{name_router_folders}"
            
            
logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)            
for file in handlers_path.glob("*.py"):
    if file.name == "__init__.py":
        continue

    module_name = f"{__package__}.{name_router_folders}.{file.stem}"
    module = import_module(module_name)

    handler_router = getattr(module, "router", None)

    if handler_router:
        router.include_router(handler_router)
        logging_data.info_logger.info(
            "\\n[Auto] Sub router inculde into {}: {}".format(router, handler_router)
        )  
    """,
    f"{DEFAULT_NAME_SETTINGS}.py": """from pydantic import BaseModel


class ModuleSettings(BaseModel):
    {SERVICE_NAME}: str = "{name}"
    {MENU_REPLY_TEXT}: str = "{name}" 
    {MENU_CALLBACK_TEXT}: str = "{name}"
    {MENU_CALLBACK_DATA}: str = "{name}"
    {SHOW_IN_MAIN_MENU}: bool = True
    {NAME_FOR_LOG_FOLDER}: str = "{log_name}"
    {NAME_FOR_TEMP_FOLDER}: str = "{temp_path}"
    {ROOT_PACKAGE}: str = "{root_package}"
    
settings: ModuleSettings = ModuleSettings()
    """,
    "response.py": """# Responses, strings, text for module {name}
from pathlib import Path

from core.module_loader.runtime.loader import get_child_modules_settings_inline_data
from app.app_utils.keyboards import get_total_buttons_inline_kb
from app.bot.core.paths import bot_path
from core.logging.api import get_loggers
from .settings import settings


logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)



inline_data = get_child_modules_settings_inline_data(
    module_path=bot_path.BOT_DIR / "modules" / Path("{path_to_module}"),
    root_package="{root_childes}",
    logging_data=logging_data,
)
if len(inline_data) >= 1:
    buttons_array = [button.text for button in inline_data]
    buttons = ", ".join(buttons_array)
    logging_data.info_logger.info(
        msg=f"[CREATE INLINE KEYBOARDS] Инлайн клавиатура для модуля test создана\\nКнопки - {buttons}"
    )

get_keyboards_menu_buttons = get_total_buttons_inline_kb(
    list_inline_kb_data=inline_data, quantity_button=1
)
""",
    "extensions.py": "# Plug-in extensions are below",
}


TEMPLATE_DIRS: List[str] = [
    "api",
    "fsm",
    "services",
    "utils",
    DEFAULT_NAME_OF_THE_ROUTER_FOLDER,
    "keyboards",
    DEFAULT_CHILD_SEPARATOR,
]
