from typing import List, Optional, Set, Dict
from dataclasses import dataclass

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.filters.admin_filters import (
    AdminDeleteExecutorCallback,
    AdminConfirmDeleteExecutorCallback,
    AdminDeleteAlbumCallback,
    AdminConfirmDeleteAlbumCallback,
    AdminDeleteSongMenuCallback,
    AdminButtonDeleteSongCallback,
    AdminConfirmDeleteSongCallback,
    AdminCancelDeleteSongCallback,
    AdminCompleteDeleteSongCallback,
    AdminScrollingSongsMenuDeleteCallback,
)
from app.bot.keyboards.inlinle import (
    get_confirmation_delete_executor_button,
    get_confirmation_delete_album_button,
    get_confirmation_delete_song_button,
    get_menu_song_delete,
    show_one_album_songs_with_base_executor,
    show_base_executor_collections,
)
from app.bot.modules.main.settings import settings as main_settings
from app.bot.modules.admin.childes.base_music.services.crud import crud_service
from app.bot.modules.admin.childes.base_music.services.base_music import (
    base_music_service,
)
from app.bot.view_model import SongResponse
from app.bot.modules.admin.utils.admin import callback_update_admin_panel_media_photo
from core.error_handlers.helpers import Result
from app.bot.response import LIMIT_SONGS, LIMIT_ALBUMS
from app.bot.utils.editing import get_info_album, get_info_executor
from app.bot.view_model import ExecutorPageRepsonse
from app.bot.response import ServerDatabaseResponse


router: Router = Router(name=__name__)

# Удаление исполнителя
@router.callback_query(StateFilter(None), AdminDeleteExecutorCallback.filter())
async def confirm_delete_base_executor(
    call: CallbackQuery,
    callback_data: AdminDeleteExecutorCallback,
) -> None:
    """Подтверждение на удаление исполнителя."""

    executor_id: int = callback_data.executor_id

    result: Result = await crud_service.get_info_executor(
        executor_id=executor_id,
    )

    if result.ok:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption=f"Вы точно хотите удалить исполнителя ?\n\n{result.data}",
            ),
            reply_markup=get_confirmation_delete_executor_button(
                executor_id=executor_id,
            ),
        )
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result.error.message
        )


@router.callback_query(StateFilter(None), AdminConfirmDeleteExecutorCallback.filter())
async def delete_executor(
    call: CallbackQuery,
    callback_data: AdminConfirmDeleteExecutorCallback,
) -> None:
    """Удаление или отмена удаления исполнителя."""

    executor_id: Optional[int] = callback_data.executor_id
    if executor_id:

        result: Result = await crud_service.delete_base_executor(
            executor_id=executor_id,
        )
        if result.ok:
            await callback_update_admin_panel_media_photo(
                call=call, caption=result.data
            )

        else:
            await callback_update_admin_panel_media_photo(
                call=call, caption=result.error.message
            )

    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption="Удаление исполнителя отменено"
        )


# Удаление альбома
@router.callback_query(StateFilter(None), AdminDeleteAlbumCallback.filter())
async def confirm_delete_album(
    call: CallbackQuery, callback_data: AdminDeleteAlbumCallback
) -> None:
    """Подтверждение на удаление альбома."""

    album_id: int = callback_data.album_id
    executor_id: int = callback_data.executor_id
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    result: Result = await crud_service.get_info_album(
        album_id=album_id,
        executor_id=executor_id,
    )
    if result.ok:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption=f"Вы точно хотите удалить альбом ?\n\n{result.data}",
            ),
            reply_markup=get_confirmation_delete_album_button(
                executor_id=callback_data.executor_id,
                album_id=callback_data.album_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ),
        )
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result.error.message
        )


@router.callback_query(StateFilter(None), AdminConfirmDeleteAlbumCallback.filter())
async def delete_album(
    call: CallbackQuery,
    callback_data: AdminConfirmDeleteAlbumCallback,
) -> None:
    """Удаление или отмена удаления альбома."""

    executor_id: Optional[int] = callback_data.executor_id
    album_id: Optional[int] = callback_data.album_id
    current_page_executor: Optional[int] = callback_data.current_page_executor
    count_pages_executor: Optional[int] = callback_data.count_pages_executor
    if executor_id and album_id:  # если альбом на удаление

        result_delete: Result = await crud_service.delete_base_album(
            executor_id=executor_id,
            album_id=album_id,
        )
        if result_delete.ok:
            result: Result = await base_music_service.show_executor(
                get_info_executor=get_info_executor,
                page_executor=current_page_executor,
            )
            await call.message.answer(text=result_delete.data)
            if result.ok:
                executor_response: ExecutorPageRepsonse = result.data
                photo_file_id: str = executor_response.executor.photo_file_id
                caption: str = executor_response.executor.info_executor

                len_list_albums = 0
                list_albums = executor_response.albums
                if list_albums:
                    len_list_albums = len(list_albums)
                    list_albums = list_albums[0:LIMIT_ALBUMS]

                await call.message.edit_media(
                    media=InputMediaPhoto(
                        media=photo_file_id,
                        caption=caption,
                    ),
                    reply_markup=show_base_executor_collections(
                        count_pages_executor=count_pages_executor,
                        current_page_executor=current_page_executor,
                        executor_id=executor_id,
                        album_position=0,
                        limit_albums=LIMIT_ALBUMS,
                        len_list_albums=len_list_albums,
                        list_albums=list_albums,
                    ),
                )
                return

            # Если произошла ошибка при возвращении к исполнителю
            await callback_update_admin_panel_media_photo(
                call=call, caption=result_delete.data
            )
        else:  # если произошла ошидка при удалении альбома
            await callback_update_admin_panel_media_photo(
                call=call, caption=result_delete.error.message
            )

    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption="Удаление альбома отменено"
        )


# Удаление песен альбома
class FSMBaseDeleteSongs(StatesGroup):
    """FSM для сценария удаления песен."""

    state_data: State = State()
    executor_id: State = State()
    current_page_executor: State = State()
    count_pages_executor: State = State()


@dataclass
class SongsDeleteResponse:
    """Хранит данные для удаления песен."""

    songs: List[SongResponse]
    selected_songs_ids: List[int]


@router.callback_query(StateFilter(None), AdminDeleteSongMenuCallback.filter())
async def menu_delete_songs(
    call: CallbackQuery,
    callback_data: AdminDeleteSongMenuCallback,
    state: FSMContext,
) -> None:
    """
    Возращает inline menu с возможность выбрать песни для удаления.
    """
    executor_id: int = callback_data.executor_id
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    album_id: int = callback_data.album_id

    result: Result = await crud_service.show_menu_songs_delete(
        album_id=album_id,
    )
    if result.ok:
        array_songs: List[SongResponse] = result.data
        len_list_songs: int = len(array_songs)

        songs: List[SongResponse] = array_songs[0:5]

        await state.update_data(
            state_data=SongsDeleteResponse(
                songs=array_songs,
                selected_songs_ids=set(),
            )
        )
        await state.update_data(current_page_executor=current_page_executor)
        await state.update_data(count_pages_executor=count_pages_executor)
        await state.update_data(executor_id=executor_id)
        await state.set_state(FSMBaseDeleteSongs.state_data)
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption="Выберите песни для удаления",
            ),
            reply_markup=get_menu_song_delete(
                list_songs=songs,
                album_id=album_id,
                len_list_songs=len_list_songs,
                song_position=0,
            ),
        ),
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result.error.message
        )


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminCancelDeleteSongCallback.filter()
)
async def cancel_delete_songs(
    call: CallbackQuery,
    callback_data: AdminCancelDeleteSongCallback,
    state: FSMContext,
):
    """Отменяет удаление песен."""
    await state.clear()

    await callback_update_admin_panel_media_photo(
        call=call,
        caption="Удаление песен отменено",
    )


@router.message(
    FSMBaseDeleteSongs.state_data,
    F.text,
)
async def get_message_from_delete_songs(
    message: Message,
):
    """Просит нажать на кнопку для отмены удаления песен при вводе текста."""

    await message.answer("Нажмите 'Отменить удаление песен' для выхода в админ панель.")


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminButtonDeleteSongCallback.filter()
)
async def delete_songs_buttons(
    call: CallbackQuery,
    callback_data: AdminButtonDeleteSongCallback,
    state: FSMContext,
):
    """Отмечает выбранную песню как готовую к удалению или снимает с удаления."""

    data: Dict = await state.get_data()
    delete_songs: Set = set(data["state_data"].selected_songs_ids)

    songs: List[SongResponse] = data["state_data"].songs
    len_list_songs: int = len(songs)  # получаем общее количество песен до изменения

    song_id: int = callback_data.song_id
    album_id: int = callback_data.album_id
    position: int = callback_data.position

    songs = songs[position : position + 5]  # измененяем песни с учетом позиции

    if song_id in delete_songs:  # если песня уже есть на удаление- убирает ее
        delete_songs.remove(song_id)
    else:  # если песни нету на удаление - добавляем ее
        delete_songs.add(song_id)

    data["state_data"].selected_songs_ids = list(delete_songs)  # сохраняем списком

    await state.update_data(state_data=data["state_data"])  # обновляем состояние

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=main_settings.DELETE_IMAGE_FILE_ID,
            caption="Выберите песни для удаления",
        ),
        reply_markup=get_menu_song_delete(
            list_songs=songs,
            delete_songs=delete_songs,
            album_id=album_id,
            song_position=position,
            limit_songs=LIMIT_SONGS,
            len_list_songs=len_list_songs,
        ),
    ),


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminScrollingSongsMenuDeleteCallback.filter()
)
async def scrolling_songe_menu_delete(
    call: CallbackQuery,
    callback_data: AdminScrollingSongsMenuDeleteCallback,
    state: FSMContext,
):
    """Пролистывает песни из меню удаления песен."""

    data: Dict = await state.get_data()

    album_id: int = callback_data.album_id
    position: int = callback_data.position + callback_data.offset
    delete_songs: Set = set(data["state_data"].selected_songs_ids)

    result: Result = await crud_service.show_menu_songs_delete(
        album_id=album_id,
    )
    if result.ok:
        songs: List[SongResponse] = result.data
        len_list_songs: int = len(songs)

        songs = songs[position : position + 5]

        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption="Выберите песни для удаления",
            ),
            reply_markup=get_menu_song_delete(
                len_list_songs=len_list_songs,
                album_id=album_id,
                song_position=position,
                limit_songs=LIMIT_SONGS,
                list_songs=songs,
                delete_songs=delete_songs,
            ),
        ),
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result.error.message
        )


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminConfirmDeleteSongCallback.filter()
)
async def confirm_delete_songs(
    call: CallbackQuery,
    callback_data: AdminConfirmDeleteSongCallback,
    state: FSMContext,
) -> None:
    """Подтверждение на удаление песен."""

    data: Dict = await state.get_data()

    delete_songs: Set = data["state_data"].selected_songs_ids

    if delete_songs:

        album_id: int = callback_data.album_id

        result: Result = await crud_service.get_positions_songs(
            album_id=album_id,
            songs_ids=delete_songs,
        )
        if result.ok:
            songs: List = result.data
            count: int = len(songs)
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=main_settings.DELETE_IMAGE_FILE_ID,
                    caption=f"Вы действительно хотите удалить песни ?"
                    f"\n\nКоличество песен: {count}\nНомера позиций песен: {str(songs)}",
                ),
                reply_markup=get_confirmation_delete_song_button(),
            )
        else:
            await state.clear()

            await callback_update_admin_panel_media_photo(
                call=call,
                caption=result.error.message,
            )

    else:
        await state.clear()

        await callback_update_admin_panel_media_photo(
            call=call,
            caption="Не было выбрано песен для удаления",
        )


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminCompleteDeleteSongCallback.filter()
)
async def delete_songs(
    call: CallbackQuery,
    callback_data: AdminCompleteDeleteSongCallback,
    state: FSMContext,
    bot: Bot,
):
    """Удаляет выбранные песни."""

    data: Dict = await state.get_data()
    executor_id = data.get("executor_id")
    current_page_executor: int = data.get("current_page_executor")
    count_pages_executor: int = data.get("count_pages_executor")

    delete_songs: List = data["state_data"].selected_songs_ids
    song: SongResponse = data["state_data"].songs[0]

    album_id: int = song.album_id

    result_delete: Result = await crud_service.delete_songs(
        album_id=album_id,
        songs_ids=delete_songs,
    )

    await state.clear()
    if result_delete.ok:  # Возвращает назад к альбому
        result: Result = await base_music_service.show_songs_with_album(
            get_info_album=get_info_album,
            album_id=album_id,
            executor_id=executor_id,
        )

        await call.message.answer(text=result_delete.data)
        if result.ok and not result.empty:  # если в альбоме есть песни
            songs: List[SongResponse] = result.data
            len_list_songs: int = len(songs)

            songs = songs[0:LIMIT_SONGS]
            back_song: SongResponse = songs[0]

            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=back_song.album_photo_file_id,
                    caption=back_song.info_album,
                ),
                reply_markup=show_one_album_songs_with_base_executor(
                    limit_songs=LIMIT_SONGS,
                    executor_id=executor_id,
                    album_id=album_id,
                    current_page_executor=current_page_executor,
                    count_pages_executor=count_pages_executor,
                    len_list_songs=len_list_songs,
                    list_songs=songs,
                    song_position=0,
                ),
            )
            return
        if result.ok and result.empty:  # Если в альбоме нет песен
            song: SongResponse = result.data

            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=song.album_photo_file_id,
                    caption=f"{song.info_album}\n\n{ServerDatabaseResponse.NOT_FOUND_SONGS.value}",
                ),
                reply_markup=show_one_album_songs_with_base_executor(
                    list_songs=[],
                    executor_id=executor_id,
                    album_id=album_id,
                    current_page_executor=current_page_executor,
                    count_pages_executor=count_pages_executor,
                ),
            )
        if not result.ok:  # если произошла ошибка
            await callback_update_admin_panel_media_photo(
                call=call, caption=result.error.message
            )

    else:
        await callback_update_admin_panel_media_photo(
            call=call,
            caption=result_delete.error.message,
        )
