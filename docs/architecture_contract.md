# System Contract

These identifiers are part of the framework contract.

Changing them requires:
- regenerating modules
- updating templates
- updating startup code (if variable not used)

## Reserved names

The following names are reserved and cannot be used
for module names or directories:

- settings
- router
- handlers
- childes
- core
- config
- main
- __init__


# Общие правила при изменении системных переменных

## 1. Изменение переменной DEFAULT_NAME_SETTINGS - core/cotracts/constants.py

**При изменении имени переменной необходимо внести изменения в**

core/contract/templates.py

<pre>"response.py": """# Responses, strings, text for module {name}
from pathlib import Path

from core.module_loader.runtime.loader import get_child_modules_settings_inline_data
from app.app_utils.keyboards import get_total_buttons_inline_kb
from app.bot.core.paths import bot_path
from core.logging.api import get_loggers
from .{new_name} import {new_name} # 1 изменение



logging_data = get_loggers(name={new_name}.NAME_FOR_LOG_FOLDER) # 2 изменение </pre>


<pre>f"{DEFAULT_NAME_ROUTER}.py": """from pathlib import Path
from importlib import import_module
from core.logging.api import get_loggers
from .{new_name} import {new_name} # 3 изменение

from aiogram import Router
        
    
router: Router = Router(name={new_name}.SERVICE_NAME) # 4 изменение

            
# Include sub router            
current_dir = Path(__file__).resolve().parent
handlers_path = current_dir / "{name_router_folders}"
            
            
logging_data = get_loggers(name={new_name}.NAME_FOR_LOG_FOLDER) # 5 изменение </pre>


<pre>f"{DEFAULT_NAME_SETTINGS}.py": """from pydantic import BaseModel

class ModuleSettings(BaseModel):
    {SERVICE_NAME}: str = "{name}"
    {MENU_REPLY_TEXT}: str = "{name}" 
    {MENU_CALLBACK_TEXT}: str = "{name}"
    {MENU_CALLBACK_DATA}: str = "{name}"
    {SHOW_IN_MAIN_MENU}: bool = True
    {NAME_FOR_LOG_FOLDER}: str = "{log_name}"
    {NAME_FOR_TEMP_FOLDER}: str = "{temp_path}"
    {ROOT_PACKAGE}: str = "{root_package}"
    
{new_name}: ModuleSettings = ModuleSettings() # 6 изменение</pre>


app/bot/modules/main/settings.py 


<pre>{new_name}: MainRouterSettings = MainRouterSettings() # 7 изменение</pre>


Изменение имени файла app/bot/modules/settings.py

<pre>{new_name}.py # 8 изменение</pre>


## 2. Изменение переменной DEFAULT_NAME_ROUTER - core/cotracts/constants.py

**При изменении имени переменной необходимо внести изменения в**

При создании нового роутера в папки hanlders, его имя должно быть таким же как у перемнной
DEFAULT_NAME_ROUTER

core/contract/templates.py

<pre>f"{DEFAULT_NAME_ROUTER}.py": """from pathlib import Path
from importlib import import_module
from core.logging.api import get_loggers
from .settings import settings

from aiogram import Router
        
    
{new_name}: Router = Router(name=settings.SERVICE_NAME) # 1 изменение

            
# Include sub router            
current_dir = Path(__file__).resolve().parent
handlers_path = current_dir / "{name_router_folders}"
            
            
logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)            
for file in handlers_path.glob("*.py"):
    if file.name == "__init__.py":
        continue

    module_name = f"{__package__}.{name_router_folders}.{file.stem}"
    module = import_module(module_name)

    handler_router = getattr(module, "{new_name}", None) # 2 изменение

    if handler_router:
        {new_name}.include_router(handler_router) # 3 изменение
        logging_data.info_logger.info(
            "\\n[Auto] Sub router inculde into {}: {}".format({new_nmae}, handler_router) # 4 изменение
        )  
    """,</pre>

app/bot/modules/main/router.py


<pre>from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters.state import StateFilter

from core.response.messages import messages


{new_name}: Router = Router(name="main") # 5 изменение


@{new_name}.message( # 6 изменение
    StateFilter(None),
    F.text == "/start",
)
async def main():</pre>

Измененее имени файла app/bot/modules/main/router.py

<pre>{new_name}.py # 7 изменение</pre>


