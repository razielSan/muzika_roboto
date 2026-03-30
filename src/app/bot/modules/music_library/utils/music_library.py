from typing import Optional

from aiogram import Bot
from aiogram.types import CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove

from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.modules.music_library.response import get_keyboards_menu_buttons


async def get_inline_menu_music_library(
    chat_id: int,
    bot: Bot,
    caption: str,
    message: Optional[str] = None,
):
    """
    Переходит к главному меню модуля music_library

    Args:
        chat_id (int): чат id бота
        bot (Bot): бот aiogram
        caption (str): текст для изображеия
        message (Optional[str], optional): Сообщение пользователю.По умолчанию не отправляется
    """

    if message:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=ReplyKeyboardRemove(),
        )
    await bot.send_photo(
        caption=caption,
        chat_id=chat_id,
        photo=music_library_settings.MENU_IMAGE_FILE_ID,
        reply_markup=get_keyboards_menu_buttons,
    )


async def callback_update_menu_inline_music_library(
    call: CallbackQuery,
    caption: str,
    message: Optional[str] = None,
):
    """
    Обновляет каллбэк запрос и переходит к главному меню модуля music_library

    Args:
        call (CallbackQuery): каллбэк aiogram
        caption (str): текст для картинки
        message (Optional[str], optional): Сообщение пользователю.По умолчанию не отправляется
    """

    if message:
        await call.answer(
            text=message,
            reply_markup=ReplyKeyboardRemove(),
        )
    await call.message.edit_media(
        media=InputMediaPhoto(
            media=music_library_settings.MENU_IMAGE_FILE_ID,
            caption=caption,
        ),
        reply_markup=get_keyboards_menu_buttons,
    )
