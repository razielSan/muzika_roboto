from aiogram import Bot
from aiogram.types import CallbackQuery, InputMediaPhoto

from app.bot.modules.admin.settings import settings as admin_settings
from app.bot.modules.admin.response import get_keyboards_menu_buttons


async def get_admin_panel(
    caption: str,
    chat_id: int,
    bot: Bot,
):
    await bot.send_photo(
        caption=caption,
        chat_id=chat_id,
        photo=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
        reply_markup=get_keyboards_menu_buttons,
    )


async def callback_update_admin_panel_media_photo(
    call: CallbackQuery,
    caption: str,
):
    await call.message.edit_media(
        media=InputMediaPhoto(
            media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
            caption=caption,
        ),
        reply_markup=get_keyboards_menu_buttons,
    )
