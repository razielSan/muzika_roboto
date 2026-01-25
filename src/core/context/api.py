from core.context.runtime import ContextRuntime
from core.context.context import AppContext


def get_app_context() -> AppContext:
    return ContextRuntime.get()
