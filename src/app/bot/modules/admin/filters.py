from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.bot.settings import settings


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message):
        return str(message.from_user.id) in settings.ADMINS_LIST
