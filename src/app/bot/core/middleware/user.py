from typing import Optional, Any

from aiogram import BaseMiddleware

from infrastructure.db.uow import UnitOfWork
from infrastructure.db.mappers.user_mapper import to_domain_user


class UserMiddleware(BaseMiddleware):
    """Middleware для возврата user."""

    async def __call__(self, handler, event, data) -> Optional[Any]:
        """Вовзращаем user."""
        telegram_id = event.from_user.id
        response_user = None
        async with UnitOfWork() as uwo:
            user = await uwo.users.get_user_by_telegram(telegram=telegram_id)
            if user:
                response_user: str = to_domain_user(user)
        data["user"] = response_user
        return await handler(event, data)
