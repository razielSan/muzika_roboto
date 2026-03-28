from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.filters import (
    BackMenuUserPanel,
    StartUserLibrary,
    StartGlobalLibrary,
)


def select_library_keyboard():
    inline_kb = InlineKeyboardBuilder()

    inline_kb.row(
        InlineKeyboardButton(
            text="🎹 Глобальная библиотека", callback_data=StartGlobalLibrary().pack()
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text="📻 Моя Библиотека", callback_data=StartUserLibrary().pack()
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel().pack(),
        )
    )

    return inline_kb.as_markup()
