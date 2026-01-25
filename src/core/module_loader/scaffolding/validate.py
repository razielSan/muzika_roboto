from pathlib import Path
from typing import List

from core.contracts.constants import (
    DEFAULT_NAME_SETTINGS,
    DEFAULT_NAME_ROUTER,
    REQUIERED_MODULE_DIRS,
)

from core.response.response_data import Result
from core.error_handlers.helpers import ok, fail
from core.contracts.module import REQUIRED_FIELDS_MODULES


def validate_module_structure(
    path: Path,
    name_settings: str = DEFAULT_NAME_SETTINGS,
    name_router: str = DEFAULT_NAME_ROUTER,
    requiered_directory: List = REQUIERED_MODULE_DIRS,
) -> Result:
    required = [f"{name_settings}.py", f"{name_router}.py"]

    for file in required:
        if not (path / file).exists():
            return fail(
                code="Invalide module",
                message=f"Invalide module structure : {file} missing",
            )
    for directory in requiered_directory:
        if not (path / directory).exists():
            return fail(
                code="Invalide module",
                message=f"Invalide module structure : {directory} directory missing",
            )

    return ok(data="success")


def validate_module_settings_file(
    path: Path,
    required_fields: set = REQUIRED_FIELDS_MODULES,
    name: str = DEFAULT_NAME_SETTINGS,
) -> Result:
    content = (path / f"{name}.py").read_text()

    for field in required_fields:
        if field not in content:
            return fail(
                code="Invalid module",
                message=f"Missing field: {field}",
            )

    return ok("success")
