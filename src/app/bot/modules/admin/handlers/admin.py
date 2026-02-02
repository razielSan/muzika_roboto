from aiogram import Router, F
from aiogram.types import Message

from app.bot.modules.admin.response import get_keyboards_menu_buttons
from app.bot.modules.admin.settings import settings
from app.bot.modules.admin.filters import AdminFilter


router = Router(name=__name__)


@router.message(
    AdminFilter(),
    F.text == f"/{settings.SERVICE_NAME}",
)
async def admin(message: Message):
    await message.answer(text="🔧 Админ Панель", reply_markup=get_keyboards_menu_buttons)
