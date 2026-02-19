from typing import List
from aiogram.types import Message
from aiogram import Bot

from app.bot.view_model import SongResponse, ExecutorPageRepsonse, AlbumResponse
from app.bot.keyboards.inlinle import (
    show_one_album_songs_with_base_executor,
    show_base_executor_collections,
)


async def open_album_pages(
    songs: List[SongResponse],
    message: Message,
    bot: Bot,
    limit_songs: int,
    album_id: int,
    executor_id: int,
    count_pages_executor: int,
    current_page_executor: int,
):
    """
    Переход на страницу к альбому с песнями.

    Args:
        songs (List[SongResponse]): Список из обьектов SongResponse
        message (Message): Обьект сообщения aiogram
        bot (Bot): Обьект bot aiogram
        limit_songs (int): Ограничение количество песен на странице
        album_id (int): Id альбома
        executor_id (int): Id исполниетля
        count_pages_executor (int): Общее количество страниц исполнителей
        current_page_executor (int): Текущая страница исполнителя
    """
    
    len_list_songs: int = len(songs)

    songs: List[AlbumResponse] = songs[0:limit_songs]
    song: SongResponse = songs[0]
    await bot.send_photo(
        chat_id=message.chat.id,
        caption=song.info_album,
        reply_markup=show_one_album_songs_with_base_executor(
            limit_songs=limit_songs,
            executor_id=executor_id,
            album_id=album_id,
            current_page_executor=current_page_executor,
            count_pages_executor=count_pages_executor,
            len_list_songs=len_list_songs,
            list_songs=songs,
            song_position=0,
        ),
        photo=song.album_photo_file_id,
    )


async def open_album_pages_with_not_songs(
    song: SongResponse,
    bot: Bot,
    message: Message,
    executor_id: int,
    album_id: int,
    message_not_songs: str,
    count_pages_executor: int,
    current_page_executor: int,
):
    """
    Переход на страницу к альбому без песен.

    Args:
        songs (List[SongResponse]): Список из обьектов SongResponse
        message (Message): Обьект сообщения aiogram
        bot (Bot): Обьект bot aiogram
        album_id (int): Id альбома
        executor_id (int): Id исполнителя
        message_not_songs (str): сообщения для вывода на страницу 
        count_pages_executor (int): Общее количество страниц исполнителей
        current_page_executor (int): Текущая страница исполнителя
    """

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=f"{song.info_album}\n\n{message_not_songs}",
        reply_markup=show_one_album_songs_with_base_executor(
            list_songs=[],
            executor_id=executor_id,
            album_id=album_id,
            current_page_executor=current_page_executor,
            count_pages_executor=count_pages_executor,
        ),
        photo=song.album_photo_file_id,
    )


async def open_executor_pages(
    executor_response: ExecutorPageRepsonse,
    message: Message,
    limit_albums: int,
    executor_id: int,
    count_pages_executor: int,
    current_page_executor: int,
    bot: Bot,
):
    """
    Переход на страницу к исолнителю.

    Args:
        executor_response (ExecutorPageRepsonse): обьект класса ExecutorPageRepsonse
        содержащий данные об исполнителеf
        message (Message): Обьект сообщения aiogram
        limit_albums (int): Ограничение количество альбомов на странице
        bot (Bot): Обьект bot aiogram
        executor_id (int): Id исполнителя
        count_pages_executor (int): Общее количество страниц исполнителей
        current_page_executor (int): Текущая страница исполнителя
    """
    len_list_albums: int = len(executor_response.albums)
    albums: List[AlbumResponse] = executor_response.albums[0:limit_albums]

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=executor_response.executor.info_executor,
        reply_markup=show_base_executor_collections(
            limit_albums=limit_albums,
            executor_id=executor_id,
            count_pages_executor=count_pages_executor,
            current_page_executor=current_page_executor,
            album_position=0,
            len_list_albums=len_list_albums,
            list_albums=albums,
        ),
        photo=executor_response.executor.photo_file_id,
    )
