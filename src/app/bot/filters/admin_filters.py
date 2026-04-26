from typing import Optional
from aiogram.filters import BaseFilter
from aiogram.types import Message

from aiogram.filters.callback_data import CallbackData
from app.bot.settings import settings


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message):
        return str(message.from_user.id) in settings.ADMINS_LIST


class AdminCreateExecutorCallback(CallbackData, prefix="admin_create_executor"):
    """Каллбэк для сценария создания только имени исполнителя"""

    pass


class AdminCreateFullExecutorCallback(
    CallbackData, prefix="admin_create_full_executor"
):
    """Каллбэк для сценария создания исполнителя с альбомами."""

    pass
