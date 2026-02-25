from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.filters import AddCallbackDataFilters


def get_buttons_for_song_collection_empty_user():
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_SONGS,
            callback_data=AddCallbackDataFilters.CollectionSong().pack(),
        )
    )
    return inline_kb.as_markup()
