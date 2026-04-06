from typing import Optional, Dict, List
from dataclasses import dataclass

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.modules.music_library.utils.music_library import (
    get_inline_menu_music_library,
)
from app.bot.settings import settings as bot_settings
from app.bot.helpers.executor import return_to_executor_page
from app.bot.helpers.album import return_to_album_page
from application.use_cases.db.music_library.update.update_photo_executor import (
    UpdatePhotoExecutor,
)
from application.use_cases.db.music_library.update.update_country_executor import (
    UpdateCountryExecutor,
)
from application.use_cases.db.music_library.update.update_genre_executor import (
    UpdateGenreExecutor,
)
from application.use_cases.db.music_library.update.update_name_executor import (
    UpdateNameExecutor,
)
from application.use_cases.db.music_library.update.update_photo_album import (
    UpdatePhotoAlbum,
)
from application.use_cases.db.music_library.update.update_year_album import (
    UpdateAlumbYear,
)
from application.use_cases.db.music_library.update.update_title_album import (
    UpdateAlumbTitle,
)
from application.use_cases.db.music_library.update.update_song_title import (
    UpdateSongTitle,
)
from domain.entities.response import LibraryMode, LibraryRole
from infrastructure.aiogram.filters import UpdateCallbackDataFilters
from infrastructure.aiogram.messages import (
    user_messages,
    LIMIT_ALBUMS,
    resolve_message,
    LIMIT_SONGS,
)
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.db.utils.editing import (
    get_information_executor,
    get_information_album,
)
from infrastructure.db.uow import UnitOfWork
from core.response.response_data import LoggingData, Result
from core.logging.api import get_loggers
from core.utils.chek import check_number_is_positivity


router: Router = Router(name=__name__)


### Обновление исполнителя

# обновления фото исполнителя


class FSMUpdateExecutorPhotoML(StatesGroup):
    """FSM для сценария обновления фотографии исполнителя."""

    music_library_executor: State = State()  # для возратка к исполнителю при отмене
    is_admin: State = State()
    user_id: State = State()
    executor_id: State = State()
    current_page_executor: State = State()
    photo: State = State()
    album_position: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.UserExecutorPhotoFileId.filter()
)
async def start_update_photo_executor(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.UserExecutorPhotoFileId,
    state: FSMContext,
):
    """Просит скинуть фотографию исполнителя."""

    executor_id: int = callback_data.excecutor_id
    user_id: Optional[int] = callback_data.user_id
    current_page_executor: int = callback_data.current_page_executor
    album_position: int = callback_data.album_position
    is_admin: bool = callback_data.is_admin

    await call.message.edit_reply_markup(reply_markup=None)

    await state.update_data(executor_id=executor_id)
    await state.update_data(user_id=user_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(album_position=album_position)
    await state.update_data(is_admin=is_admin)
    await state.update_data(music_library_executor=True)
    await state.set_state(FSMUpdateExecutorPhotoML.photo)
    await call.message.answer(
        text=user_messages.DROP_THE_PHOTO,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateExecutorPhotoML.photo, F.photo)
async def end_update_photo_executor(
    message: Message,
    state: FSMContext,
    bot,
):
    """Обновляет фотографию исполнителя."""

    photo_file_id: str = message.photo[-1].file_id
    photo_file_unique_id: str = message.photo[-1].file_unique_id

    chat_id: int = message.chat.id
    update_photo_executor_data = await state.get_data()
    executor_id: int = update_photo_executor_data.get("executor_id")
    user_id: Optional[int] = update_photo_executor_data.get("user_id")
    current_page_executor: int = update_photo_executor_data.get("current_page_executor")
    album_position: int = update_photo_executor_data.get("album_position")
    is_admin: bool = update_photo_executor_data.get("is_admin")
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    await state.clear()
    result_update_photo_executor: Result = await UpdatePhotoExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        user_id=user_id,
        executor_id=executor_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
    )
    if result_update_photo_executor.ok:
        result_message: str = resolve_message(code=result_update_photo_executor.code)
        role: LibraryMode.role = LibraryRole.ADMIN if is_admin else LibraryRole.USER
        await return_to_executor_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            limit_albums=LIMIT_ALBUMS,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            get_information_executor=get_information_executor,
            uow=UnitOfWork,
            album_position=album_position,
            mode=LibraryMode(
                user_id=user_id,
                role=role,
            ),
        )
        return

    if not result_update_photo_executor.ok:
        error_message = resolve_message(code=result_update_photo_executor.error.code)
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMUpdateExecutorPhotoML.photo)
async def end_update_photo_executor_message(message: Message):
    """Отравляет сообщение если были отправлены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="фото")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.USER_CANCEL_BUTTON.value
        )
    )


# обновление страны исполнителя


class FSMUpdateCountryExecutorML(StatesGroup):
    """FSM для сценария обновления страны исполнителя."""

    music_library_executor: State = State()  # для возратка к исполнителю при отмене
    is_admin: State = State()
    user_id: State = State()
    executor_id: State = State()
    current_page_executor: State = State()
    country: State = State()
    album_position: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.UserExecutorCountry.filter()
)
async def start_update_country_executor(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.UserExecutorCountry,
    state: FSMContext,
):
    """Просит ввести страну исполнителя."""

    await call.message.edit_reply_markup(reply_markup=None)

    user_id: Optional[int] = callback_data.user_id
    executor_id: int = callback_data.excecutor_id
    current_page_executor: int = callback_data.current_page_executor
    album_position: int = callback_data.album_position
    is_admin: bool = callback_data.is_admin

    await state.update_data(user_id=user_id)
    await state.update_data(executor_id=executor_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(album_position=album_position)
    await state.update_data(is_admin=is_admin)
    await state.update_data(music_library_executor=True)
    await state.set_state(FSMUpdateCountryExecutorML.country)

    await call.message.answer(
        text=user_messages.ENTER_THE_СOUNTRY_EXECUTOR,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateCountryExecutorML.country, F.text)
async def end_update_country_executor(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет страну исполнителя."""

    update_country_executor_data: Dict = await state.get_data()
    executor_id: int = update_country_executor_data.get("executor_id")
    album_position: int = update_country_executor_data.get("album_position")
    user_id: Optional[int] = update_country_executor_data.get("user_id")
    current_page_executor: int = update_country_executor_data.get(
        "current_page_executor"
    )
    is_admin: bool = update_country_executor_data.get("is_admin")
    chat_id: int = message.chat.id
    country: str = message.text.strip()
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result_update_country_executor: Result = await UpdateCountryExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        user_id=user_id,
        executor_id=executor_id,
        country=country,
    )
    if result_update_country_executor.ok:
        await state.clear()
        role: LibraryMode.role = LibraryRole.ADMIN if is_admin else LibraryRole.USER
        result_message: str = resolve_message(code=result_update_country_executor.code)
        await return_to_executor_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            limit_albums=LIMIT_ALBUMS,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            get_information_executor=get_information_executor,
            uow=UnitOfWork,
            album_position=album_position,
            mode=LibraryMode(
                user_id=user_id,
                role=role,
            ),
        )
        return

    if not result_update_country_executor.ok:
        error_message: str = resolve_message(
            code=result_update_country_executor.error.code
        )
        await message.answer(
            text=f"{error_message}\n\n{user_messages.ENTER_THE_СOUNTRY_EXECUTOR}"
        )


@router.message(FSMUpdateCountryExecutorML.country)
async def end_update_country_executor_message(message: Message):
    """Отравляет сообщение если были отправлены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.USER_CANCEL_BUTTON.value
        )
    )


# Обновление жанров исполнителя
class FSMUpdateGenresExecutorML(StatesGroup):
    """FSM для сценария обновления жанров исполнителя."""

    music_library_executor: State = State()  # для возратка к исполнителю при отмене
    is_admin: State = State()
    user_id: State = State()
    executor_id: State = State()
    album_position: State = State()
    current_page_executor: State = State()
    genres: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.UserExecutorGenres.filter()
)
async def start_update_executor_genres(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.UserExecutorGenres,
    state: FSMContext,
):
    "Просит ввести жанры исполнителя."

    await call.message.edit_reply_markup(reply_markup=None)

    user_id: Optional[int] = callback_data.user_id
    executor_id: int = callback_data.excecutor_id
    current_page_executor: int = callback_data.current_page_executor
    album_position: int = callback_data.album_position
    is_admin: bool = callback_data.is_admin

    await state.update_data(user_id=user_id)
    await state.update_data(executor_id=executor_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(album_position=album_position)
    await state.update_data(is_admin=is_admin)
    await state.update_data(music_library_executor=True)
    await state.set_state(FSMUpdateGenresExecutorML.genres)
    await call.message.answer(
        text=user_messages.ENTER_THE_GENRES,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateGenresExecutorML.genres, F.text)
async def end_update_genres_executor(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет жанры исполнителя."""

    update_genres_executor_data: Dict = await state.get_data()
    executor_id: int = update_genres_executor_data.get("executor_id")
    album_position: int = update_genres_executor_data.get("album_position")
    user_id: Optional[int] = update_genres_executor_data.get("user_id")
    current_page_executor: int = update_genres_executor_data.get(
        "current_page_executor"
    )
    is_admin: bool = update_genres_executor_data.get("is_admin")
    chat_id: int = message.chat.id
    genres: List[str] = message.text.split(".")
    genres = [genre.strip() for genre in genres]
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )
    await state.clear()
    result_update_country_executor: Result = await UpdateGenreExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        user_id=user_id,
        executor_id=executor_id,
        genres=genres,
    )
    if result_update_country_executor.ok:
        result_message: str = resolve_message(code=result_update_country_executor.code)
        role: LibraryMode.role = LibraryRole.ADMIN if is_admin else LibraryRole.USER
        await return_to_executor_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            limit_albums=LIMIT_ALBUMS,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            get_information_executor=get_information_executor,
            uow=UnitOfWork,
            album_position=album_position,
            mode=LibraryMode(
                user_id=user_id,
                role=role,
            ),
        )
        return
    if not result_update_country_executor.ok:
        error_message: str = resolve_message(
            code=result_update_country_executor.error.code
        )
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMUpdateGenresExecutorML.genres)
async def end_update_genres_executor_message(message: Message):
    """Отравляет сообщение если были отправлены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.USER_CANCEL_BUTTON.value
        )
    )


# обновляет имя исполнителя
class FSMUpdateNameExecutorML(StatesGroup):
    """FSM для сценария для обновления имения исполнителя."""

    music_library_executor: State = State()  # для возратка к исполнителю при отмене
    is_admin: State = State()
    current_page_executor: State = State()
    album_position: State = State()
    user_id: State = State()
    executor_id: State = State()
    name: State = State()
    country: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.UserExecutorName.filter()
)
async def start_update_name_executor(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.UserExecutorName,
    state: FSMContext,
):
    """Просит ввести имя исполнителя."""

    executor_id: int = callback_data.excecutor_id
    user_id: Optional[int] = callback_data.user_id
    country: str = callback_data.country
    current_page_executor: int = callback_data.current_page_executor
    album_position: int = callback_data.album_position
    is_admin: bool = callback_data.is_admin

    await call.message.edit_reply_markup(reply_markup=None)

    await state.update_data(executor_id=executor_id)
    await state.update_data(user_id=user_id)
    await state.update_data(country=country)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(album_position=album_position)
    await state.update_data(is_admin=is_admin)
    await state.update_data(music_library_executor=True)
    await state.set_state(FSMUpdateNameExecutorML.name)
    await call.message.answer(
        text=user_messages.ENTER_THE_EXECUTOR_NAME,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateNameExecutorML.name, F.text)
async def end_update_name_excutor(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет имя исполнителя."""

    name: str = message.text.strip()
    update_name_executor_data: Dict = await state.get_data()
    executor_id: int = update_name_executor_data.get("executor_id")
    user_id: Optional[int] = update_name_executor_data.get("user_id")
    country: str = update_name_executor_data.get("country")
    is_admin: bool = update_name_executor_data.get("is_admin")
    chat_id: int = message.chat.id
    album_position: int = update_name_executor_data.get("album_position")
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )
    result_update_name_executor: Result = await UpdateNameExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        user_id=user_id,
        executor_id=executor_id,
        name=name,
        country=country,
        is_admin=is_admin,
    )
    if result_update_name_executor.ok:
        await state.clear()
        result_message: str = resolve_message(code=result_update_name_executor.code)
        current_page_executor: int = result_update_name_executor.data
        role: LibraryMode.role = LibraryRole.ADMIN if is_admin else LibraryRole.USER
        await return_to_executor_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            limit_albums=LIMIT_ALBUMS,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            get_information_executor=get_information_executor,
            uow=UnitOfWork,
            album_position=album_position,
            mode=LibraryMode(
                user_id=user_id,
                role=role,
            ),
        )
        return
    if not result_update_name_executor.ok:
        error_message: str = resolve_message(
            code=result_update_name_executor.error.code
        )
        await message.answer(
            text=f"{error_message}\n\n{user_messages.ENTER_THE_EXECUTOR_NAME}"
        )


@router.message(FSMUpdateNameExecutorML.name)
async def end_update_name_executor_message(message: Message):
    """Отравляет сообщение если были отправлены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.USER_CANCEL_BUTTON.value
        )
    )


###  Обновление альбома

# Обновление фото альбома


class FSMUpdatePhotoAlbumML(StatesGroup):
    """FSM для сценария обновления фото альбома."""

    current_page_executor: State = State()
    music_library_album: State = State()
    executor_id: State = State()
    user_id: State = State()
    album_id: State = State()
    is_global_executor: State = State()
    album_position: State = State()
    is_admin: State = State()
    photo: State = State()


@dataclass
class UpdatePhotoAlbumData:
    current_page_executor: int
    music_library_album: bool
    executor_id: int
    user_id: Optional[int]
    album_id: int
    is_global_executor: bool
    is_admin: bool
    album_position: int
    photo: None


@router.callback_query(StateFilter(None), UpdateCallbackDataFilters.AlbumPhoto.filter())
async def start_update_photo_album(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.AlbumPhoto,
    state: FSMContext,
):
    """Просит скинуть фотография для обновления."""

    current_page_executor: int = callback_data.current_page_executor
    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    album_id: int = callback_data.album_id
    is_admin: bool = callback_data.is_admin
    album_position: int = callback_data.album_position
    is_global_executor: bool = callback_data.is_global_executor
    await state.update_data(
        UpdatePhotoAlbumData(
            current_page_executor=current_page_executor,
            music_library_album=True,
            executor_id=executor_id,
            user_id=user_id,
            album_id=album_id,
            is_global_executor=is_global_executor,
            album_position=album_position,
            is_admin=is_admin,
            photo=None,
        ).__dict__
    )

    await call.message.edit_reply_markup(reply_markup=None)

    await state.set_state(FSMUpdatePhotoAlbumML.photo)
    await call.message.answer(
        text=user_messages.DROP_THE_PHOTO,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdatePhotoAlbumML.photo, F.photo)
async def end_update_photo_album(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет фото альбома."""

    data: Dict = await state.update_data()
    state_data: UpdatePhotoAlbumData = UpdatePhotoAlbumData(**data)

    chat_id: int = message.chat.id
    photo_file_id: str = message.photo[-1].file_id
    photo_file_unique_id: str = message.photo[-1].file_unique_id
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result = await UpdatePhotoAlbum(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        album_id=state_data.album_id,
        executor_id=state_data.executor_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
    )
    await state.clear()
    if result.ok:
        result_message: str = resolve_message(result.code)

        await return_to_album_page(
            chat_id=chat_id,
            bot=bot,
            current_page_executor=state_data.current_page_executor,
            message=result_message,
            logging_data=logging_data,
            uow=UnitOfWork,
            album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
            get_information_album=get_information_album,
            limit_songs=LIMIT_SONGS,
            song_position=0,
            album_position=state_data.album_position,
            executor_id=state_data.executor_id,
            user_id=state_data.user_id,
            album_id=state_data.album_id,
            is_global_executor=state_data.is_global_executor,
            is_admin=state_data.is_admin,
        )

    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMUpdatePhotoAlbumML.photo)
async def end_update_photo_album_message(message: Message):
    """Отправляет сообщение если были введены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="фото")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.USER_CANCEL_BUTTON.value
        )
    )


# Обновление года альбома
class FSMUpdateAlbumYearML(StatesGroup):
    """FSM для сценария обновления года альбома."""

    current_page_executor: State = State()
    music_library_album: State = State()
    executor_id: State = State()
    user_id: State = State()
    album_id: State = State()
    is_global_executor: State = State()
    album_position: State = State()
    is_admin: State = State()
    year: State = State()


@dataclass
class UpdateAlbumYearData:
    current_page_executor: int
    music_library_album: bool
    executor_id: int
    user_id: Optional[int]
    album_id: int
    is_global_executor: bool
    album_position: int
    is_admin: bool
    year: None


@router.callback_query(StateFilter(None), UpdateCallbackDataFilters.AlbumYear.filter())
async def start_update_year_album(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.AlbumYear,
    state: FSMContext,
):
    """Просит ввести год альбома"""

    current_page_executor: int = callback_data.current_page_executor
    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    album_id: int = callback_data.album_id
    album_position: int = callback_data.album_position
    is_global_executor: bool = callback_data.is_global_executor
    is_admin: bool = callback_data.is_admin

    await state.update_data(
        UpdateAlbumYearData(
            current_page_executor=current_page_executor,
            music_library_album=True,
            executor_id=executor_id,
            user_id=user_id,
            album_id=album_id,
            is_global_executor=is_global_executor,
            album_position=album_position,
            is_admin=is_admin,
            year=None,
        ).__dict__
    )
    await state.set_state(FSMUpdateAlbumYearML.year)

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=user_messages.ENTER_THE_ALBUM_YEAR,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateAlbumYearML.year, F.text)
async def end_update_year_album(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет год альбома."""

    result_year: Result = check_number_is_positivity(number=message.text.strip())
    if not result_year.ok:  # если год был указан не верно
        await message.answer(
            text=f"{result_year.error.message}\n\n{user_messages.ENTER_THE_ALBUM_YEAR}"
        )
        return
    year: int = result_year.data
    data: Dict = await state.get_data()
    state_data: UpdateAlbumYearData = UpdateAlbumYearData(**data)
    chat_id: int = message.chat.id

    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result: Result = await UpdateAlumbYear(
        logging_data=logging_data, uow=UnitOfWork()
    ).execute(
        executor_id=state_data.executor_id,
        album_id=state_data.album_id,
        year=year,
    )
    await state.clear()
    if result.ok:
        result_message: str = resolve_message(code=result.code)
        await return_to_album_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            uow=UnitOfWork,
            logging_data=logging_data,
            current_page_executor=state_data.current_page_executor,
            album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
            limit_songs=LIMIT_SONGS,
            get_information_album=get_information_album,
            album_id=state_data.album_id,
            executor_id=state_data.executor_id,
            user_id=state_data.user_id,
            album_position=state_data.album_position,
            song_position=0,
            is_global_executor=state_data.is_global_executor,
            is_admin=state_data.is_admin,
        )
        return
    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMUpdateAlbumYearML.year)
async def end_update_year_album_message(message: Message):
    """Отправляет сообщение если были введены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.USER_CANCEL_BUTTON.value
        )
    )


# обновления заголовка альбома
class FSMUpdateAlbumTitleML(StatesGroup):
    """FSM для сценария обновления заголовка альбома."""

    current_page_executor: State = State()
    music_library_album: State = State()
    executor_id: State = State()
    user_id: State = State()
    album_id: State = State()
    is_global_executor: State = State()
    album_position: State = State()
    is_admin: State()
    title: State = State()


@dataclass
class UpdateAlbumTitleData:
    current_page_executor: int
    music_library_album: bool
    executor_id: int
    user_id: Optional[int]
    album_id: int
    is_global_executor: bool
    album_position: int
    is_admin: bool
    title: None


@router.callback_query(StateFilter(None), UpdateCallbackDataFilters.AlbumTitle.filter())
async def start_update_title_album(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.AlbumTitle,
    state: FSMContext,
):
    """Просит ввести заголовок альбома"""

    current_page_executor: int = callback_data.current_page_executor
    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    album_id: int = callback_data.album_id
    album_position: int = callback_data.album_position
    is_global_executor: bool = callback_data.is_global_executor
    is_admin: bool = callback_data.is_admin

    await state.update_data(
        UpdateAlbumTitleData(
            current_page_executor=current_page_executor,
            music_library_album=True,
            executor_id=executor_id,
            user_id=user_id,
            album_id=album_id,
            is_global_executor=is_global_executor,
            album_position=album_position,
            is_admin=is_admin,
            title=None,
        ).__dict__
    )
    await state.set_state(FSMUpdateAlbumTitleML.title)

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=user_messages.ENTER_THE_ALBUM_TITLE,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateAlbumTitleML.title, F.text)
async def end_update_title_album(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет заголовок альбома."""

    title: str = message.text.strip()
    data: Dict = await state.get_data()
    state_data: UpdateAlbumTitleData = UpdateAlbumTitleData(**data)
    chat_id: int = message.chat.id

    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result: Result = await UpdateAlumbTitle(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        album_id=state_data.album_id,
        executor_id=state_data.executor_id,
        title=title,
    )
    if result.ok:
        await state.clear()
        result_message: str = resolve_message(code=result.code)
        await return_to_album_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            uow=UnitOfWork,
            logging_data=logging_data,
            current_page_executor=state_data.current_page_executor,
            album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
            limit_songs=LIMIT_SONGS,
            get_information_album=get_information_album,
            album_id=state_data.album_id,
            executor_id=state_data.executor_id,
            user_id=state_data.user_id,
            album_position=state_data.album_position,
            song_position=0,
            is_global_executor=state_data.is_global_executor,
            is_admin=state_data.is_admin,
        )
    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        await message.answer(
            text=f"{error_message}\n\n{user_messages.ENTER_THE_ALBUM_TITLE}"
        )


@router.message(FSMUpdateAlbumTitleML.title)
async def end_update_title_album_message(message: Message):
    """Отправляет сообщение если были введены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.USER_CANCEL_BUTTON.value
        )
    )


# обновления имени песеи
class FSMUpdateTitleSong(StatesGroup):
    """FSM для сценария обновления имени песнм."""

    current_page_executor: State = State()
    music_library_album: State = State()
    executor_id: State = State()
    user_id: State = State()
    album_id: State = State()
    is_global_executor: State = State()
    album_position: State = State()
    position: State = State()
    is_admin: State = State()
    title: State = State()


@dataclass
class UpdateTitleSongData:
    current_page_executor: int
    music_library_album: bool
    executor_id: int
    user_id: Optional[int]
    album_id: int
    is_global_executor: bool
    album_position: int
    position: int
    is_admin: bool
    title: None


@router.callback_query(StateFilter(None), UpdateCallbackDataFilters.SongTitle.filter())
async def start_update_song_title(
    call: CallbackQuery, callback_data: FSMUpdateTitleSong, state: FSMContext
):
    """Просит ввести позицию песни."""

    await call.message.edit_reply_markup(reply_markup=None)

    current_page_executor: int = callback_data.current_page_executor
    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    album_id: int = callback_data.album_id
    album_position: int = callback_data.album_position
    is_global_executor: bool = callback_data.is_global_executor
    is_admin: bool = callback_data.is_admin

    await state.update_data(
        UpdateTitleSongData(
            current_page_executor=current_page_executor,
            music_library_album=True,
            executor_id=executor_id,
            user_id=user_id,
            album_id=album_id,
            album_position=album_position,
            is_global_executor=is_global_executor,
            is_admin=is_admin,
            position=0,
            title=None,
        ).__dict__
    )
    await state.set_state(FSMUpdateTitleSong.position)

    await call.message.answer(
        text=user_messages.ENTER_THE_SONG_POSITION,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateTitleSong.position, F.text)
async def add_position_song(message: Message, state: FSMContext):
    """
    Просит ввести имя песни.

    Добавляет позицию песни в FSM.
    """

    result_position: Result = check_number_is_positivity(number=message.text.strip())
    if not result_position.ok:
        error_message: str = result_position.error.message
        await message.answer(
            text=f"{error_message}\n\n{user_messages.ENTER_THE_SONG_POSITION}"
        )
        return
    position: int = result_position.data
    await state.update_data(position=position)
    await state.set_state(FSMUpdateTitleSong.title)
    await message.answer(text=user_messages.ENTER_THE_SONG_NAME)


@router.message(FSMUpdateTitleSong.position)
async def add_position_song_message(message: Message):
    """Отправляет сообщение при вводе не тех данных."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.USER_CANCEL_BUTTON.value
        )
    )


@router.message(FSMUpdateTitleSong.title, F.text)
async def end_update_song_title(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет имя песни."""

    data: Dict = await state.get_data()
    state_data: UpdateTitleSongData = UpdateTitleSongData(**data)
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )
    chat_id: int = message.chat.id
    title: str = message.text.strip()

    result: Result = await UpdateSongTitle(
        uow=UnitOfWork(),
        logging_data=logging_data,
    ).execute(
        album_id=state_data.album_id,
        position=state_data.position,
        title=title,
    )
    if result.ok:
        if result.empty:
            await state.set_state(FSMUpdateTitleSong.position)

            not_found_message: str = resolve_message(code=result.code)
            await message.answer(
                text=not_found_message.format(position=state_data.position)
            )
            await message.answer(text=user_messages.ENTER_THE_SONG_POSITION)
            return

        await state.clear()
        result_message: str = resolve_message(code=result.code)
        result_message: str = result_message.format(title=title)
        await return_to_album_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            uow=UnitOfWork,
            logging_data=logging_data,
            current_page_executor=state_data.current_page_executor,
            album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
            limit_songs=LIMIT_SONGS,
            get_information_album=get_information_album,
            album_id=state_data.album_id,
            executor_id=state_data.executor_id,
            user_id=state_data.user_id,
            album_position=state_data.album_position,
            song_position=0,
            is_global_executor=state_data.is_global_executor,
            is_admin=state_data.is_admin,
        )
    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMUpdateTitleSong.title)
async def end_update_song_title_message(message: Message):
    """Отправляет сообщение при вводе не тех данных."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.USER_CANCEL_BUTTON.value
        )
    )
