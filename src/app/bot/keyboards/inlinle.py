from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from app.bot.filters.admin_filters import (
    AdminCreateFullExecutorCallback,
    AdminCreateExecutorCallback,
)

from app.bot.modules.music_library.childes.executor.settings import settings
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.filters import (
    StartGlobalLibrary,
    Search,
    BackAdminMenuCallback,
)


def get_buttons_create_executor():
    """Кнопки для выбора создания исполнителя или исполнителя с альбомами."""

    inline_kb = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CREATE_EXECUTOR.value,
            callback_data=AdminCreateExecutorCallback().pack(),
        )
    )
    inline_kb.row(
        (
            InlineKeyboardButton(
                text=KeyboardResponse.CREATE_EXECUTOR_WITH_ALBUMS.value,
                callback_data=AdminCreateFullExecutorCallback().pack(),
            )
        )
    )
    inline_kb.row(
        (
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_ADMIN_PANEL.value,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    )
    return inline_kb.as_markup()


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
            callback_data=BackAdminMenuCallback().pack(),
        )
    )

    return inline_kb.as_markup()
