from typing import List

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from core.response.messages import messages


def get_reply_add_executor_button() -> ReplyKeyboardMarkup:
    reply_kb: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    reply_kb.add(KeyboardButton(text=messages.UNKNOWN_TEXT))
    reply_kb.row(KeyboardButton(text=messages.CANCEL_TEXT))

    return reply_kb.as_markup(resize_keyboard=True)
