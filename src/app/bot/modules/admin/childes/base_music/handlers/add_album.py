from typing import List, Dict

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.admin.childes.base_music.filters import AdminAddAlbumCallback
from app.bot.modules.admin.childes.base_music.services.crud import crud_service
from app.bot.modules.admin.childes.base_music.services.base_music import (
    base_music_service,
)
from app.bot.utils.delete import delete_previous_message
from app.bot.view_model import SongResponse
from core.response.messages import messages
from app.app_utils.keyboards import get_reply_cancel_button
from app.bot.utils.editing import get_info_album
from app.bot.utils.navigator import (
    open_album_pages,
    open_album_pages_with_not_songs,
)
from app.bot.response import LIMIT_SONGS
from core.response.response_data import Result
from app.bot.modules.admin.utils.admin import get_admin_panel
from core.utils.chek import check_number_is_positivity
from app.app_utils.keyboards import get_reply_cancel_button
from app.bot.utils.delete import delete_previous_message
from app.bot.settings import settings as bot_settings
from app.bot.response import ServerDatabaseResponse


router: Router = Router(name=__name__)


# Добавление песен в альбом
class FSMAddAlbum(StatesGroup):
    """FSM для сценария добавления альбома с песнями."""

    current_page_executor: State = State()
    count_pages_executor: State = State()
    unique_titles_songs: State = State()  # провекра на уникальность заголовоков
    album_title: State = State()
    song_title: State = State()
    executor_id: State = State()
    year: State = State()
    songs: State = State()
    processings: State = State()


@router.callback_query(StateFilter(None), AdminAddAlbumCallback.filter())
async def start_add_album(
    call: CallbackQuery,
    callback_data: AdminAddAlbumCallback,
    state: FSMContext,
):
    """Просит ввести название альбома."""

    await call.message.edit_reply_markup(reply_markup=None)

    executor_id: int = callback_data.executor_id
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    await call.message.answer(
        "Введите название альбома",
        reply_markup=get_reply_cancel_button(),
    )
    await state.update_data(executor_id=executor_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(count_pages_executor=count_pages_executor)

    await state.set_state(FSMAddAlbum.album_title)


@router.message(FSMAddAlbum.album_title, F.text)
async def add_title(message: Message, state: FSMContext, bot: Bot):
    """Просит пользователя ввести год выпуска альбома."""

    await delete_previous_message(message=message, bot=bot)

    album_title: str = message.text
    await state.update_data(album_title=album_title)
    await state.set_state(FSMAddAlbum.year)

    await message.answer("Введите год выпуска альбома")


@router.message(FSMAddAlbum.album_title)
async def add_title_message(message: Message):
    """Присылает сообщение если введены не те данные."""

    await message.answer(
        "Название альбома должно быть в формате"
        " текст\n\nВведите, снова, название альбома"
    )


@router.message(FSMAddAlbum.year, F.text)
async def add_year(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """
    Просит пользователя скинуть песни для добавления в альбома и отправляет
    клавиатуру для подтверждения.
    """

    await delete_previous_message(message=messages, bot=bot)
    year_result: Result = check_number_is_positivity(number=message.text)

    if not year_result.ok:
        await message.answer(
            text=f"{year_result.error.message}\n\n" "Введите,снова,год выпуска альбома"
        )
        return

    year: int = year_result.data
    await state.update_data(year=year)
    await state.update_data(songs=[])
    await state.update_data(unique_titles_songs=[])
    await state.set_state(FSMAddAlbum.songs)

    await message.answer(
        text="Скидывайте песни"
        f" для добавления в альбом\n\n{messages.CONFIRMATION_TEXT}: Подтверждение добавления песен'"
        f"\n{messages.CANCEL_TEXT}: Отмена добавления песен",
        reply_markup=get_reply_cancel_button(
            optional_button_text=messages.CONFIRMATION_TEXT,
        ),
    )


@router.message(FSMAddAlbum.year)
async def add_year_message(message: Message):
    """Отправляет сообщение если были введены не те данные."""

    await message.answer(
        "Год выпуска альбома должен быть в числовом формате"
        "\n\nВведите, снова, название год выпуска альбома"
    )


@router.message(FSMAddAlbum.songs, F.audio)
async def add_songs_audio_album(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Добавляет песни в список для сохранения."""

    song_title: str = message.audio.file_name.split(".")[0].strip()
    file_id: str = message.audio.file_id
    file_unique_id: str = message.audio.file_unique_id

    data: Dict = await state.get_data()
    unique_titles_songs: List[str] = data["unique_titles_songs"]
    songs: List = data["songs"]
    if (
        song_title in unique_titles_songs
    ):  # Если песня с таким названием уже была добавлена
        await message.answer(text=f"Уже была сохранена песня с названием {song_title}")
        return

    songs.append(
        SongResponse(file_id=file_id, file_unique_id=file_unique_id, title=song_title),
    )
    unique_titles_songs.append(song_title)
    await state.update_data(songs=songs)
    await state.update_data(unique_titles_songs=unique_titles_songs)

    await message.answer(text=f"Песня {song_title} сохранена")


@router.message(FSMAddAlbum.songs, F.text == messages.CONFIRMATION_TEXT)
async def add_songs_album_confirm(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Просит подтвердить или отменить добавление песен."""

    await delete_previous_message(bot=bot, message=message)

    data: Dict = await state.get_data()
    album_title: str = data.get("album_title")
    year: str = data.get("year")

    songs = data["songs"]
    if len(songs) == 0:  # если не было добавлено песен
        await message.answer(
            "Нет песен для добавления\n\n"
            "Скидывайте,снова, песни для добавления в альбом"
        )
        return

    await state.set_state(FSMAddAlbum.processings)
    await message.answer(
        f"Будет создан альбом\n\n({year}) {album_title}\nКоличество песен: {len(songs)}\n\n"
        f"{messages.CONFIRMATION_TEXT}: Подтверждение добавления песен\n"
        f"{messages.CANCEL_TEXT}: Отмена добавления песен"
    )


@router.message(FSMAddAlbum.songs)
async def add_songs_album_message(
    message: Message,
):
    """Отправляет сообщение если были отправлены не те данные"""
    await message.answer(
        text="Скидываемые данные должные быть в аудио формате"
        "\n\nСкидывайте,снова,песни для добваления в альбом"
    )


@router.message(FSMAddAlbum.processings, F.text == messages.CONFIRMATION_TEXT)
async def finish_add_songs_album(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Сохраняет альбом."""

    await delete_previous_message(bot=bot, message=message)

    data: Dict = await state.get_data()
    executor_id: int = data.get("executor_id")
    album_title: str = data.get("album_title")
    year: int = data.get("year")
    count_pages_executor: int = data.get("count_pages_executor")
    current_page_executor: int = data.get("current_page_executor")
    songs: List[SongResponse] = data.get("songs")

    result_add_albums: Result = await crud_service.create_album(
        executor_id=executor_id,
        title=album_title,
        year=year,
        photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
        photo_file_unique_id=bot_settings.ALBUM_DEFAULT_PHOTO_UNIQUE_ID,
        songs=songs,
    )

    await state.clear()
    if result_add_albums.ok:  # если альбом был создан

        album_id: int = result_add_albums.data
        result: Result = await base_music_service.show_songs_with_album(
            executor_id=executor_id, album_id=album_id, get_info_album=get_info_album
        )
        await message.answer(text=ServerDatabaseResponse.SUCCESS_ADD_ALBUM)
        if result.ok and not result.empty:  # для возврата на страницу альбома
            await open_album_pages(
                songs=result.data,
                message=message,
                limit_songs=LIMIT_SONGS,
                album_id=album_id,
                executor_id=executor_id,
                count_pages_executor=count_pages_executor,
                current_page_executor=current_page_executor,
                bot=bot,
            )

            return

        if result.ok and result.empty:  # если в альбоме нет песен
            song = result.data

            await open_album_pages_with_not_songs(
                song=song,
                bot=bot,
                message=message,
                executor_id=executor_id,
                album_id=album_id,
                count_pages_executor=count_pages_executor,
                current_page_executor=current_page_executor,
                message_not_songs=ServerDatabaseResponse.NOT_FOUND_SONGS.value,
            )
            return

        if not result.ok:
            await get_admin_panel(
                caption=result.error.message,
                chat_id=message.chat.id,
                bot=bot,
            )
            return

    # если произошла ошибка при добавлении песен
    await get_admin_panel(
        chat_id=message.chat.id,
        caption=result_add_albums.error.message,
        bot=bot,
    )


@router.message(FSMAddAlbum.processings)
async def finish_add_songs_message(
    message: Message,
):
    """
    Отправляет сообщение, в состоянии подтверждения добавления альбома, если было
    введено что то кроме подтверждения или отмены добавления.
    """

    await message.answer(
        f"Нажмите\n\n{messages.CONFIRMATION_TEXT}: Подверждение добавления песен"
        f"\n{messages.CANCEL_TEXT}: Отмена добавления песен"
    )
