from typing import Optional, List

from aiogram import Bot
from aiogram.types import CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove


from app.bot.modules.music_library.settings import settings as music_library_settings
from infrastructure.aiogram.keyboards.inline import (
    get_buttons_for_song_collection_user,
    get_buttons_for_song_collection_empty_user,
)
from domain.entities.response import (
    UserCollectionSongsResponse,
    CollectionSongsResponse,
)
from infrastructure.aiogram.messages import user_messages


async def show_user_collection(
    bot: Bot,
    chat_id: int,
    user_response: UserCollectionSongsResponse,
    start_collection_songs: int,
    limit_collection_songs: int,
    caption: str,
    is_admin: bool = False,
    message: Optional[str] = None,
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
    """
    # Выставляем обложку сборника песен
    photo_file_id: str = music_library_settings.COLLECTION_SONGS_PHOTO_FILE_ID
    if user_response.collection_songs_photo_file_id:
        photo_file_id: str = user_response.collection_songs_photo_file_id

    if message:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=ReplyKeyboardRemove(),
        )

    if not user_response.collection_songs:  # если нет песен в сборнике
        await bot.send_photo(
            chat_id=chat_id,
            caption=f"{user_messages.THERE_ARE_NO_SONGS}",
            photo=photo_file_id,
            reply_markup=get_buttons_for_song_collection_empty_user(),
        )
        return

    collection_songs = user_response.collection_songs

    len_collection_songs: int = len(collection_songs)

    collection_songs: List[CollectionSongsResponse] = collection_songs[
        start_collection_songs : start_collection_songs + limit_collection_songs
    ]  # для показа необходимого количества песен на странице

    await bot.send_photo(
        chat_id=chat_id,
        caption=caption,
        photo=photo_file_id,
        reply_markup=get_buttons_for_song_collection_user(
            colellection_songs=collection_songs,
            len_collection_songs=len_collection_songs,
            song_position=start_collection_songs,
            limit_songs=limit_collection_songs,
            is_admin=is_admin,
        ),
    )


async def callback_show_user_collection(
    call: CallbackQuery,
    user_response: UserCollectionSongsResponse,
    start_collection_songs: int,
    limit_collection_songs: int,
    caption: str,
    is_admin: bool = False,
    message: str = None,
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
        caption (str): текст для изображения

    """
    if message:
        await call.answer(text=message)

    # Выставляем обложку сборника песен
    photo_file_id: str = music_library_settings.COLLECTION_SONGS_PHOTO_FILE_ID
    if user_response.collection_songs_photo_file_id:
        photo_file_id: str = user_response.collection_songs_photo_file_id

    if not user_response.collection_songs:  # если нет песен в сборнике
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=photo_file_id,
                caption=f"{user_messages.THERE_ARE_NO_SONGS}",
            ),
            reply_markup=get_buttons_for_song_collection_empty_user(
                is_admin=is_admin,
            ),
        )
        return

    collection_songs: List[CollectionSongsResponse] = user_response.collection_songs

    len_collection_songs: int = len(collection_songs)
    collection_songs = collection_songs[
        start_collection_songs : start_collection_songs + limit_collection_songs
    ]  # для показа необходимого количества песен на странице
    await call.message.edit_media(
        media=InputMediaPhoto(
            media=photo_file_id,
            caption=caption,
        ),
        reply_markup=get_buttons_for_song_collection_user(
            colellection_songs=collection_songs,
            len_collection_songs=len_collection_songs,
            limit_songs=limit_collection_songs,
            song_position=start_collection_songs,
        ),
    )
