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
)


def select_library_keyboard():
    inline_kb = InlineKeyboardBuilder()

    inline_kb.row(
        InlineKeyboardButton(
            text=settings.SEARCH_EXECUTOR,
            callback_data=Search.Executor().pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=settings.GLOBAL_LIBRARY_NAME, callback_data=StartGlobalLibrary().pack()
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=settings.USER_LIBRARY_NAME, callback_data=StartUserLibrary().pack()
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel().pack(),
        )
    )

    return inline_kb.as_markup()


def select_search_keyboard():

    inline_kb = InlineKeyboardBuilder()

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.SEARCH_BY_NAME,
            callback_data=Search.ExecutorName().pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.SEARCH_BY_GENRES,
            callback_data=Search.ExecutorGenres().pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel().pack(),
        )
    )

    return inline_kb.as_markup()


def select_executor_genres_keybord(
    quantity_button: int = 1,
):
    inline_kb = InlineKeyboardBuilder()

    for order, genre in GENRES.items():
        inline_kb.add(
            InlineKeyboardButton(
                text=genre,
                callback_data=Search.ExecutorGenreButton(order=order).pack(),
            )
        )
    inline_kb.adjust(quantity_button)

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
):
    inline_kb = InlineKeyboardBuilder()

    for executor in executors:
        inline_kb.row(
            InlineKeyboardButton(
                text=f"{executor.name} ({executor.country})",
                callback_data=Search.ExecutorButton(id=executor.id).pack(),
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
                ).pack(),
            )
        )
    inline_kb.row(*page.items)

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel().pack(),
        )
    )

    return inline_kb.as_markup()
