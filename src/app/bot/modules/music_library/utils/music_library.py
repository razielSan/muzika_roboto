from typing import Optional, List

from aiogram import Bot
from aiogram.types import CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove

from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.modules.music_library.response import get_keyboards_menu_buttons
from infrastructure.aiogram.keyboards.inline import get_buttons_for_song_collection_user
from domain.entities.response import UserCollectionSongResponse, CollectionSongResponse


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
        await call.message.answer(
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


async def show_user_collection(
    bot: Bot,
    chat_id: int,
    user_response: UserCollectionSongResponse,
    start_collection_song: int,
    limit_collection_song: int,
    photo_file_id: str,
    caption: str,
    message: Optional[str] = None,
    song_position: int = 0,
):
    """
    Переходит к сборнику песен пользователя

    Args:
        bot (Bot): бот aiogram
        chat_id (int): чат id бота
        user_response (UserCollectionSongResponse): Обьект класса UserCollectionSongResponse

        aтрибуты UserCollectionSongResponse:
            - collection_songs (List[CollectionSongResponse])
            - collection_song_photo_unique_id (Optional[str])
            - collection_song_photo_file_id  (Optional[str])

        start_collection_song (int): Начало выборки песен
        limit_collection_song (int): Максимальное количество песен на странице сборника
        photo_file_id (str): Id картинки сборника песен
        caption (str): текст для изображения
        message (Optional[str], optional): Сообщение пользователю.По умолчанию не отправляется
        song_position (int, optional): Позиция песни.По умолчанию 0
    """

    collection_songs = user_response.collection_songs

    len_collection_songs: int = len(collection_songs)

    collection_songs: List[CollectionSongResponse] = collection_songs[
        start_collection_song : start_collection_song + limit_collection_song
    ]  # для показа необходимого количества песен на странице

    if message:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=ReplyKeyboardRemove(),
        )

    await bot.send_photo(
        chat_id=chat_id,
        caption=caption,
        photo=photo_file_id,
        reply_markup=get_buttons_for_song_collection_user(
            colellection_songs=collection_songs,
            len_collection_songs=len_collection_songs,
            song_position=song_position,
            limit_songs=limit_collection_song,
        ),
    )


async def callback_show_user_collection(
    call: CallbackQuery,
    user_response: UserCollectionSongResponse,
    start_collection_song: int,
    limit_collection_song: int,
    photo_file_id: str,
    caption: str,
    song_position: int = 0,
):
    """
    Обновляет каллбэк запрос и переходит к сборнику песен пользователя

    Args:
        call: Каллбэк aiogram
        user_response (UserCollectionSongResponse): Обьект класса UserCollectionSongResponse

        aтрибуты UserCollectionSongResponse:
            - collection_songs (List[CollectionSongResponse])
            - collection_song_photo_unique_id (Optional[str])
            - collection_song_photo_file_id  (Optional[str])

        start_collection_song (int): Начало выборки песен
        limit_collection_song (int): Максимальное количество песен на странице сборника
        photo_file_id (str): Id картинки сборника песен
        caption (str): текст для изображения
        song_position (int, optional): Позиция песни.По умолчанию 0
    """
    collection_songs = user_response.collection_songs

    len_collection_songs = len(collection_songs)

    collection_songs = collection_songs[
        start_collection_song : start_collection_song + limit_collection_song
    ]  # для показа необходимого количества песен на странице
    await call.message.edit_media(
        media=InputMediaPhoto(
            media=photo_file_id,
            caption=caption,
        ),
        reply_markup=get_buttons_for_song_collection_user(
            colellection_songs=collection_songs,
            len_collection_songs=len_collection_songs,
            limit_songs=limit_collection_song,
            song_position=song_position,
        ),
    )
