from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter

from app.bot.modules.admin.childes.base_music.settings import settings
from app.bot.keyboards.inlinle import select_admin_library_keyboard
from app.bot.modules.admin.settings import settings as admin_settings
from core.response.messages import messages


router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def base_music(
    call: CallbackQuery,
) -> None:
    """Возвращает клавиатуры выбора библиотеки админа."""

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
            caption=messages.ADMIN_PANEL_TEXT,
        ),
        reply_markup=select_admin_library_keyboard(is_admin=True),
    )
