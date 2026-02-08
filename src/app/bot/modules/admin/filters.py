from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.filters.callback_data import CallbackData

from app.bot.settings import settings


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message):
        return str(message.from_user.id) in settings.ADMINS_LIST


class BackAdminMenuCallback(CallbackData, prefix="back_admin_menu"):
    pass
