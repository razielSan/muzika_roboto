from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.modules.music_library.childes.executor.settings import settings
from domain.entities.response import ExecutorSearchResponse, Page
from infrastructure.aiogram.messages import GENRES
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.filters import (
    BackMenuUserPanel,
    StartUserLibrary,
    StartGlobalLibrary,
    Search,
    ScrollingCallbackDataFilters,
    BackAdminMenuCallback,
)


def select_library_keyboard(
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
            text=settings.USER_LIBRARY_NAME, callback_data=StartUserLibrary().pack()
        )
    )

    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackMenuUserPanel().pack(),
            )
        )

    return inline_kb.as_markup()


def select_search_keyboard(
    is_admin: bool,
):

    inline_kb = InlineKeyboardBuilder()

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.SEARCH_BY_NAME,
            callback_data=Search.ExecutorName(is_admin=is_admin).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.SEARCH_BY_GENRES,
            callback_data=Search.ExecutorGenres(is_admin=is_admin).pack(),
        )
    )

    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackMenuUserPanel().pack(),
            )
        )
    return inline_kb.as_markup()


def select_executor_genres_keybord(
    is_admin: bool,
    quantity_button: int = 1,
):
    inline_kb = InlineKeyboardBuilder()

    for order, genre in GENRES.items():
        inline_kb.add(
            InlineKeyboardButton(
                text=genre,
                callback_data=Search.ExecutorGenreButton(
                    order=order,
                    is_admin=is_admin,
                ).pack(),
            )
        )
    inline_kb.adjust(quantity_button)

    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackMenuUserPanel().pack(),
            )
        )
    return inline_kb.as_markup()


def show_executor_search(
    executors: List[ExecutorSearchResponse],
    position: int,
    total: int,
    limit: int,
    is_admin: bool,
):
    inline_kb = InlineKeyboardBuilder()

    for executor in executors:
        inline_kb.row(
            InlineKeyboardButton(
                text=f"{executor.name} ({executor.country})",
                callback_data=Search.ExecutorButton(
                    id=executor.id,
                    is_admin=is_admin,
                ).pack(),
            )
        )

    page = Page(
        items=[],
        position=position,
        total=total,
        limit=limit,
    )
    if page.has_prev:
        page.items.append(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_BUTTON,
                callback_data=ScrollingCallbackDataFilters.SearchExecutor(
                    position=position,
                    offset=-limit,
                    is_admin=is_admin,
                ).pack(),
            )
        )
    if page.has_next:
        page.items.append(
            InlineKeyboardButton(
                text=KeyboardResponse.FORWARD_BUTTON,
                callback_data=ScrollingCallbackDataFilters.SearchExecutor(
                    position=position,
                    offset=limit,
                    is_admin=is_admin,
                ).pack(),
            )
        )
    inline_kb.row(*page.items)

    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackMenuUserPanel().pack(),
            )
        )

    return inline_kb.as_markup()
