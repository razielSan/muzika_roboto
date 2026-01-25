from typing import List, Dict

from core.response.modules_loader import ModuleInfo
from core.response.response_data import LoggingData
from core.contracts.constants import DEFAULT_NAME_ROUTER


def register_module(
    dp: object,
    modules: List[ModuleInfo],
    logging_data: LoggingData,
    name: str = DEFAULT_NAME_ROUTER,
) -> None:
    """
    Подключает к диспетчеру переданные роутеры.


    Args:
        dp (Dispatcher): Диспетчер aiogram
        modules (List[ModuleInfo]): Список содержащий в себе обьект класса ModuleInfo
        для подключения router
        logging_data (LoggingData): Обьект класса LoggingData

        атрибуты LoggingData:
            - info_logger (Logger)
            - warning_logger (Logger)
            - error_logger (Logger)
            - critical_logger (Logger)
            - router_name (str)
        
        name (str): Имя переменной для роутера

    """

    root: List[ModuleInfo] = sorted(
        [m for m in modules if m.is_root], key=lambda m: m.root
    )
    children: List[ModuleInfo] = sorted(
        [m for m in modules if not m.is_root], key=lambda m: m.module_depth
    )
    children = sorted(
        children,
        key=lambda m: m.parent,
    )

    root_map: Dict = {}

    for mod in root:
        router = mod.router
        root_router = getattr(router, name)
        dp.include_router(router=root_router)
        root_map[mod.root] = root_router
        logging_data.info_logger.info(
            "\n[Auto] Root router inculde into dp: {}".format(root_router)
        )

    for mod in children:
        parent_router = root_map.get(mod.parent)
        if not parent_router:
            continue
        
        router = mod.router
        child_router = getattr(router, name)
        parent_router.include_router(child_router)
        logging_data.info_logger.info(
            f"\n[Auto] Child router inculded into {parent_router}: {child_router}",
        )
