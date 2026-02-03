from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters.state import StateFilter

from app.bot.modules.admin.response import get_keyboards_menu_buttons
from app.bot.modules.admin.settings import settings
from app.bot.modules.admin.filters import AdminFilter


router = Router(name=__name__)


@router.message(
    AdminFilter(),
    F.text == f"/{settings.SERVICE_NAME}",
    StateFilter(None),
)
async def admin(
    message: Message,
    bot: Bot,
):

    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    await bot.send_photo(
        chat_id=message.chat.id,
        caption="🔧 Админ Панель",
        reply_markup=get_keyboards_menu_buttons,
        photo=settings.ADMIN_PANEL_PHOTO_FILE_ID,
    )
