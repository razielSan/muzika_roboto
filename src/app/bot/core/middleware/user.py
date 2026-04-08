from typing import Optional, Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext

from domain.errors.error_code import NotFoundCode
from domain.entities.db.models.user import User as UserDomain
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.messages import resolve_message
from infrastructure.db.mappers.user_mapper import to_domain_user


class UserMiddleware(BaseMiddleware):
    """Middleware для возврата user."""

    async def __call__(
        self,
        handler,
        event,
        data,
    ) -> Optional[Any]:
        """Вовзращает user."""
        telegram_id: int = event.from_user.id

        async with UnitOfWork() as uwo:
            user: UserDomain = await uwo.users.get_user_by_telegram(
                telegram=telegram_id
            )
            if not user:  # если пользователь не найден
                name: str = event.from_user.first_name
                user = await uwo.users.create_user(
                    name=name,
                    telegram=telegram_id,
                )
                state: FSMContext = data.get("state")
                
                await state.clear()
                error_message: str = resolve_message(
                    code=NotFoundCode.USER_NOT_FOUND.name
                )
                if hasattr(event, "message"):  # если каллбэк событие
                    return await event.message.answer(text=error_message)
                else:
                    return await event.answer(text=error_message)
            response_user: UserDomain = to_domain_user(model=user)
        data["user"] = response_user
        return await handler(event, data)
