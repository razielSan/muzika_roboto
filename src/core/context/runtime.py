from core.context.context import AppContext


class ContextRuntime:
    _ctx: AppContext = None

    @classmethod
    def init(cls, ctx: AppContext):
        if cls._ctx is not None:
            raise RuntimeError("Context already initialized")
        cls._ctx = ctx

    @classmethod
    def get(cls) -> AppContext:
        if cls._ctx is None:
            raise RuntimeError("Context not initialized")
        return cls._ctx


