from typing import List
import sys

from core.scripts.bot.create_module import creates_new_modules_via_the_command_line
from core.scripts.bot.remove_module import remove_module
from core.paths.paths import SRC_DIR
from core.context.context import load_bot_paths
from core.contracts.constants import DEFAULT_BOT_MODULES_ROOT


def main() -> None:
    """
    Команды для командной строки.

    cli add-module <имя модуля>- Создание модулей
    cli remove-module <имя модуля> - Удаление модуля
    """

    list_sys_argv: List[str] = sys.argv

    if len(list_sys_argv) < 2:
        print(
            "-----\nИспользование:\n\ncli add-module "
            "<name module> - Создание модуля\n"
            "cli remove-module <name module> - Удаление модуля\n-----"
        )
        sys.exit()

    command: str = list_sys_argv[1]

    bot_path = load_bot_paths(bot_core="app.bot.core.paths")

    if command == "add-module":
        if len(list_sys_argv) < 3:
            print(
                "-----\nУкажите имя модуля.\n\nДочерний модуль должен быть "
                "разделен '.'\n\nПример:\nсli add-module test.data.test\n-----"
            )
            exit()
        elif len(list_sys_argv) >= 4:
            print(
                "-----\nЗа раз можно создать только один модуль\n\n"
                "Пример:\ncli add-module test.test\n-----"
            )
            exit()
        else:
            print("Идет создание модуля...")
            creates_new_modules_via_the_command_line(
                root_dir=SRC_DIR,
                module_name=list_sys_argv[2],
                root_package=DEFAULT_BOT_MODULES_ROOT,
            )
    elif command == "remove-module":
        if len(list_sys_argv) < 3:
            print(
                "-----\nУкажите путь до модуля.\n\nДочерний модуль должен быть "
                "разделен '.'\n\nПример:\n"
                "\ncli remove-module test.data\n-----"
            )
            exit()
        elif len(list_sys_argv) >= 4:
            print(
                "-----\nЗа раз можно удалить только один модуль\n\n"
                "Пример:\ncli remove-module test.test\n-----"
            )
            exit()
        else:
            name_module: str = list_sys_argv[2]
            remove_module(
                name_module=name_module,
                log_path=bot_path.LOG_DIR,
                temp_path=bot_path.TEMP_DIR,
                root_package=DEFAULT_BOT_MODULES_ROOT,
                root_dir=SRC_DIR,
            )
            print(f"Процедура удаления {name_module} завершена")
    elif command == "help":
        print(
            """-----
Доступные команды:
              
cli add-module <name_module> - Создание модуля
cli remove-module <name_module> - Удаление модуля
----
"""
        )
    else:
        print("Неизвестная команда\n\ncli help - Основные команды")
