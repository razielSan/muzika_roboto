from typing import Optional

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from infrastructure.aiogram.response import KeyboardResponse


def get_reply_cancel_button(
    optional_button_text: Optional[str] = None,
    cancel_button: str = KeyboardResponse.USER_CANCEL_BUTTON.value,
) -> ReplyKeyboardMarkup:
    """Reply кнопка отмены."""
    reply_kb: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    if optional_button_text:
        reply_kb.row(KeyboardButton(text=optional_button_text))

    reply_kb.row(KeyboardButton(text=cancel_button))
    return reply_kb.as_markup(resize_keyboard=True)
