from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.modules.music_library.childes.executor.settings import settings
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.filters import (
    BackMenuUserPanel,
    StartGlobalLibrary,
    Search,
)


def select_admin_library_keyboard(
    is_admin: bool,
):
    inline_kb = InlineKeyboardBuilder()

    inline_kb.row(
        InlineKeyboardButton(
            text=settings.SEARCH_EXECUTOR,
            callback_data=Search.Executor(is_admin=is_admin).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=settings.GLOBAL_LIBRARY_NAME,
            callback_data=StartGlobalLibrary(
                is_admin=is_admin,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel(
                is_admin=is_admin,
            ).pack(),
        )
    )

    return inline_kb.as_markup()
