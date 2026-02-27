from typing import Optional

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from infrastructure.aiogram.messages import user_messages


def get_reply_cancel_button(
    cancel_text: str = user_messages.USER_CANCEL_TEXT,
    optional_button_text: Optional[str] = None,
) -> ReplyKeyboardMarkup:
    """Reply кнопка отмены."""
    reply_kb: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    if optional_button_text:
        reply_kb.row(KeyboardButton(text=optional_button_text))
    reply_kb.row(KeyboardButton(text=cancel_text))
    return reply_kb.as_markup(resize_keyboard=True)
