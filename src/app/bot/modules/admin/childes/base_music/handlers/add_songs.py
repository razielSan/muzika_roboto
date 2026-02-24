from typing import List, Dict

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.filters.admin_filters import AdminAddSongsCallback
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
from app.bot.response import ServerDatabaseResponse


router: Router = Router(name=__name__)


# Добавление аидио записей в альбом
class FSMAddSongs(StatesGroup):
    """FSM для сценария добавления песен в альбом."""

    current_page_executor: State = State()
    count_pages_executor: State = State()
    counter: State = State()
    executor_id: State = State()
    album_id: State = State()
    titles: State = State()
    songs: State = State()
    processings: State = State()
    counter: State = State()


@router.callback_query(StateFilter(None), AdminAddSongsCallback.filter())
async def start_add_songs(
    call: CallbackQuery,
    callback_data: AdminAddSongsCallback,
    state: FSMContext,
):
    """Просит скинуть песня для добавления в альбом и отправляет клавиатуру для подтверждения."""

    await call.message.edit_reply_markup(reply_markup=None)

    album_id: int = callback_data.album_id
    executor_id: int = callback_data.executor_id
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    await call.message.answer(
        text="Скидывайте песни"
        f" для добавления в альбом\n\n{messages.CONFIRMATION_TEXT}: Подтверждение добавления песен"
        f"\n{messages.CANCEL_TEXT}: Отмена добавления песен",
        reply_markup=get_reply_cancel_button(
            optional_button_text=messages.CONFIRMATION_TEXT,
        ),
    )

    await state.set_state(FSMAddSongs.songs)
    await state.update_data(songs=[])
    await state.update_data(titles=[])
    await state.update_data(album_id=album_id)
    await state.update_data(executor_id=executor_id)
    await state.update_data(counter=0)
    await state.update_data(count_pages_executor=count_pages_executor)
    await state.update_data(current_page_executor=current_page_executor)


@router.message(FSMAddSongs.songs, F.audio)
@router.message(FSMAddSongs.songs, F.voice)
async def add_songs_audio(
    message: Message,
    state: FSMContext,
):
    """Добавляет песни в список для сохранения."""

    data: Dict = await state.get_data()
    counter: int = data.get("counter")
    if message.voice:
        counter += 1
        title = f"{messages.UNKNOWN_TITLE_TEXT} {counter}"
        file_id: str = message.voice.file_id
        file_unique_id: str = message.voice.file_unique_id

    if message.audio:
        title: str = message.audio.file_name.split(".")[0].strip()
        file_id: str = message.audio.file_id
        file_unique_id: str = message.audio.file_unique_id

    titles: List[str] = data["titles"]
    songs: List[SongResponse] = data["songs"]
    if title in titles:  # Если песня с таким названием уже была добавлена
        await message.answer(text=f"Уже была сохранена песня с названием {title}")
    else:
        songs.append(
            SongResponse(file_id=file_id, file_unique_id=file_unique_id, title=title),
        )
        await message.answer(text=f"Песня {title} сохранена")
        titles.append(title)
        await state.update_data(songs=songs)
        await state.update_data(counter=counter)
        await state.update_data(titles=titles)


@router.message(FSMAddSongs.songs, F.text == messages.CONFIRMATION_TEXT)
async def add_songs_confirm(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Просит подтвердить песни для удаления."""

    await delete_previous_message(bot=bot, message=message)

    data: Dict = await state.get_data()

    songs: List[SongResponse] = data["songs"]
    if len(songs) == 0:  # если не было добавлено песен
        await message.answer(
            "Нет песен для добавления\n\n"
            "Скидывайте,снова, песни для добавления в альбом\n"
            f"{messages.CONFIRMATION_TEXT}: Подтверждение добавления песен"
            f"\n{messages.CANCEL_TEXT}: Отмена добавления песен"
        )
        return

    await state.set_state(FSMAddSongs.processings)
    await message.answer(
        f"Будут добавлены песни\n\nКоличество: {len(songs)}\n"
        f"{messages.CONFIRMATION_TEXT}: Подтверждение добавления песен\n"
        f"{messages.CANCEL_TEXT}: Отмена добавления песен"
    )


@router.message(FSMAddSongs.songs)
async def add_songs_message(
    message: Message,
):
    """Отправляет сообщение если были отправлены данные не в том формате."""

    await message.answer(
        text="Скидываемые данные должные быть в аудио формате"
        "\n\nСкидывайте,снова,песни для добваления в альбом\n"
        f"{messages.CONFIRMATION_TEXT}: Подтверждение добавления песен"
        f"\n{messages.CANCEL_TEXT}: Отмена добавления песен"
    )


@router.message(FSMAddSongs.processings, F.text == messages.CONFIRMATION_TEXT)
async def finish_add_songs(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Сохраняет песни в альбом."""

    await delete_previous_message(bot=bot, message=message)

    data: Dict = await state.get_data()
    album_id: int = data.get("album_id")
    executor_id: int = data.get("executor_id")
    count_pages_executor: int = data.get("count_pages_executor")
    current_page_executor: int = data.get("current_page_executor")
    songs: List[SongResponse] = data.get("songs")

    result_add_songs: Result = await crud_service.add_songs(
        album_id=album_id,
        songs=songs,
    )

    await state.clear()
    if result_add_songs.ok:  # Если песни были сохранены
        result: Result = await base_music_service.show_songs_with_album(
            executor_id=executor_id, album_id=album_id, get_info_album=get_info_album
        )
        await message.answer(
            text=ServerDatabaseResponse.SUCCESS_ADD_SONGS,
            reply_markup=ReplyKeyboardRemove(),
        )
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

        if result and result.empty:  # если в альбоме нет песен
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

    if not result_add_songs.ok:  # если произошла ошибка при добавлении песен
        msg: str = result_add_songs.error.message
        await message.answer(
            text=msg,
            reply_markup=ReplyKeyboardRemove(),
        )

        await get_admin_panel(
            chat_id=message.chat.id,
            caption=msg,
            bot=bot,
        )


@router.message(FSMAddSongs.processings)
async def finish_add_songs_message(
    message: Message,
):
    """
    Отправляет сообщение, в состоянии подтверждения добавления песен, если было
    введено что то кроме подтверждения или отмены добавления.
    """

    await message.answer(
        f"Выберите один из вариантов\n\n{messages.CONFIRMATION_TEXT}: Подверждение добавления песен"
        f"\n{messages.CANCEL_TEXT}: Отмена добавления песен"
    )
