from pathlib import Path
from importlib import import_module
from core.logging.api import get_loggers
from .settings import settings

from aiogram import Router
        
    
router: Router = Router(name=settings.SERVICE_NAME)

            
# Include sub router            
current_dir = Path(__file__).resolve().parent
handlers_path = current_dir / "handlers"
            
            
logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)            
for file in handlers_path.glob("*.py"):
    if file.name == "__init__.py":
        continue

    module_name = f"{__package__}.handlers.{file.stem}"
    module = import_module(module_name)

    handler_router = getattr(module, "router", None)

    if handler_router:
        router.include_router(handler_router)
        logging_data.info_logger.info(
            "\n[Auto] Sub router inculde into {}: {}".format(router, handler_router)
        )  
    