from typing import Dict, List

from aiogram import Router, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.modules.admin.childes.base_music.filters import (
    AdminUpdatePhotoExecutorCallback,
    AdminUpdatePhotoAlbumCallback,
    AdminUpdateExecutorNameCallback,
    AdminUpdateExecutorCountryCallback,
    AdminUpdateAlbumTitleCallback,
    AdminUpdateAlbumYearCallback,
    AdminUpdateExecutorGenresCallback,
)
from app.app_utils.keyboards import get_reply_cancel_button
from app.bot.modules.admin.childes.base_music.settings import settings
from core.response.messages import messages
from core.logging.api import get_loggers
from core.utils.chek import check_number_is_positivity
from app.bot.modules.admin.childes.base_music.services.crud import crud_service
from app.bot.modules.admin.utils.admin import get_admin_panel
from app.bot.utils.delete import delete_previous_message
from core.response.response_data import LoggingData, Result


router: Router = Router(name=__name__)


# Обновление фото исполнителя
class FSMUpdatePhotoExecutor(StatesGroup):
    """FSM для сценария удаления фото исполнителя."""

    executor_id: State = State()
    photo: State = State()
    processing: State = State()


@router.callback_query(StateFilter(None), AdminUpdatePhotoExecutorCallback.filter())
async def start_update_executor_photo(
    call: CallbackQuery,
    callback_data: AdminUpdatePhotoExecutorCallback,
    state: FSMContext,
    bot: Bot,
):
    """Просит пользователя скинуть фото исполнителя для обновления."""

    await call.message.edit_reply_markup(reply_markup=None)

    executor_id: int = callback_data.executor_id

    await call.message.answer(
        f"Скидывайте фото исполнителя или нажмите '{messages.CANCEL_TEXT}'",
        reply_markup=get_reply_cancel_button(),
    )
    await state.update_data(executor_id=executor_id)
    await state.set_state(FSMUpdatePhotoExecutor.photo)


@router.message(FSMUpdatePhotoExecutor.photo)
async def finish_update_executor_photo(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет фото исполнителя."""

    await delete_previous_message(bot=bot, message=message)

    if message.photo:

        await state.set_state(FSMUpdatePhotoExecutor.processing)

        await message.answer(text=messages.WAIT_MESSAGE)

        data: Dict = await state.get_data()

        logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
        executor_id: int = data["executor_id"]
        photo_file_id: str = message.photo[-1].file_id
        photo_file_unique_id: str = message.photo[-1].file_unique_id
        chat_id: int = message.chat.id

        result_update: Result = await crud_service.update_photo_executor(
            executor_id=executor_id,
            photo_file_id=photo_file_id,
            photo_file_unique_id=photo_file_unique_id,
            logging_data=logging_data,
        )
        await state.clear()
        if result_update.ok:
            await get_admin_panel(
                caption=result_update.data,
                chat_id=chat_id,
                bot=bot,
            )
        else:
            await get_admin_panel(
                chat_id=chat_id,
                caption=result_update.error.message,
                bot=bot,
            )
    else:
        await message.answer(
            text="Данные должны быть"
            " изображением\n\nСкидывайте,снова, фото"
            f" исполнителя или нажмите '{messages.CANCEL_TEXT}'"
        )


# Обновление фото альбома
class FSMUpdatePhotoAlmum(StatesGroup):
    """FSM для сценария обновления фото альбома."""

    executor_id: State = State()
    album_id: State = State()
    photo: State = State()
    processing: State = State()


@router.callback_query(StateFilter(None), AdminUpdatePhotoAlbumCallback.filter())
async def start_update_album_photo(
    call: CallbackQuery,
    callback_data: AdminUpdatePhotoAlbumCallback,
    state: FSMContext,
    bot: Bot,
):
    """Просит пользователя скинуть фото для обновления альбома."""

    await call.message.edit_reply_markup(reply_markup=None)

    executor_id: int = callback_data.executor_id
    album_id: int = callback_data.album_id

    await call.message.answer(
        f"Скидывайте фото альбома или нажмите '{messages.CANCEL_TEXT}'",
        reply_markup=get_reply_cancel_button(),
    )
    await state.update_data(executor_id=executor_id)
    await state.update_data(album_id=album_id)
    await state.set_state(FSMUpdatePhotoAlmum.photo)


@router.message(FSMUpdatePhotoAlmum.photo)
async def finish_update_album_photo(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет фото альбома."""

    await delete_previous_message(bot=bot, message=message)

    if message.photo:
        await state.set_state(FSMUpdatePhotoExecutor.processing)

        await message.answer(
            text=messages.WAIT_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
        data: Dict = await state.get_data()

        executor_id: int = data["executor_id"]
        album_id: int = data["album_id"]
        photo_file_id: str = message.photo[-1].file_id
        photo_file_unique_id: str = message.photo[-1].file_unique_id
        chat_id: int = message.chat.id

        result_update_photo_album: Result = await crud_service.update_album_photo(
            executor_id=executor_id,
            album_id=album_id,
            logging_data=logging_data,
            photo_file_id=photo_file_id,
            photo_file_unique_id=photo_file_unique_id,
        )
        await state.clear()
        if result_update_photo_album.ok:
            await get_admin_panel(
                caption=result_update_photo_album.data,
                chat_id=chat_id,
                bot=bot,
            )
        else:
            await get_admin_panel(
                chat_id=chat_id,
                caption=result_update_photo_album.error.message,
                bot=bot,
            )

    else:
        await message.answer(
            text="Данные должны быть"
            " изображением\n\nСкидывайте,снова, фото"
            f" альбома или нажмите '{messages.CANCEL_TEXT}'"
        )


# Обновление имени исполнителя
class FSMUpdateExecutorName(StatesGroup):
    """FSM для сценария обновления имени исполнителя."""

    executor_id: State = State()
    name: State = State()


@router.callback_query(StateFilter(None), AdminUpdateExecutorNameCallback.filter())
async def start_update_excutor_name(
    call: CallbackQuery,
    callback_data: AdminUpdateExecutorNameCallback,
    state: FSMContext,
):
    """Просит ввести имя исплнителя."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        f"Введите имя исполнителя или нажмите '{messages.CANCEL_TEXT}'",
        reply_markup=get_reply_cancel_button(),
    )

    executor_id: int = callback_data.executor_id
    await state.update_data(executor_id=executor_id)
    await state.set_state(FSMUpdateExecutorName.name)


@router.message(FSMUpdateExecutorName.name)
async def finish_update_executor_name(message: Message, state: FSMContext, bot: Bot):
    """Обновляет имя исполнителя."""

    if message.text:
        await message.answer(
            text=messages.WAIT_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        name: str = message.text.strip().lower()
        chat_id: int = message.chat.id

        result_update_executor_name: Result = await crud_service.update_executor_name(
            executor_id=executor_id, name=name, logging_data=logging_data
        )
        await state.clear()
        if result_update_executor_name.ok:
            await get_admin_panel(
                caption=result_update_executor_name.data,
                chat_id=chat_id,
                bot=bot,
            )
        else:
            await get_admin_panel(
                caption=result_update_executor_name.error.message,
                chat_id=chat_id,
                bot=bot,
            )

    else:
        await message.answer(
            text="Данные должны быть"
            " текстом\n\nВведите,снова, имя исполнителя"
            f" или нажмите '{messages.CANCEL_TEXT}'"
        )


# Обновление страны исполнителя
class FSMUpdateExecutorCountry(StatesGroup):
    """FSM для сценария обновления страны исполнителя."""

    executor_id: State = State()
    country: State = State()


@router.callback_query(StateFilter(None), AdminUpdateExecutorCountryCallback.filter())
async def start_update_excutor_country(
    call: CallbackQuery,
    callback_data: AdminUpdateExecutorCountryCallback,
    state: FSMContext,
):
    """Просит ввести страну исполнителя."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        f"Введите страну исполнителя или нажмите '{messages.CANCEL_TEXT}'",
        reply_markup=get_reply_cancel_button(),
    )

    executor_id: int = callback_data.executor_id
    await state.update_data(executor_id=executor_id)
    await state.set_state(FSMUpdateExecutorCountry.country)


@router.message(FSMUpdateExecutorCountry.country)
async def finish_update_executor_country(message: Message, state: FSMContext, bot: Bot):
    """Обновляет страну исполнителя."""
    if message.text:
        await message.answer(
            text=messages.WAIT_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        country: str = message.text.strip().lower()
        chat_id: int = message.chat.id

        result_update_executor_country: Result = (
            await crud_service.update_executor_country(
                executor_id=executor_id,
                country=country,
                logging_data=logging_data,
            )
        )

        await state.clear()
        if result_update_executor_country.ok:
            await get_admin_panel(
                caption=result_update_executor_country.data,
                chat_id=chat_id,
                bot=bot,
            )
        else:
            await get_admin_panel(
                caption=result_update_executor_country.error.message,
                chat_id=chat_id,
                bot=bot,
            )
    else:
        await message.answer(
            text="Данные должны быть"
            " текстом\n\nВведите,снова, страну исполнителя"
            f" или нажмите '{messages.CANCEL_TEXT}'"
        )


# Обновление заголовок альбома
class FSMUpdateAlbumTitle(StatesGroup):
    """ "FSM для обновления заголовка альбома."""

    executor_id: State = State()
    album_id: State = State()
    title: State = State()


@router.callback_query(StateFilter(None), AdminUpdateAlbumTitleCallback.filter())
async def start_update_album_tilte(
    call: CallbackQuery,
    callback_data: AdminUpdateAlbumTitleCallback,
    state: FSMContext,
):
    """Просит ввести заголовок альбома."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        f"Введите название альбома или нажмите '{messages.CANCEL_TEXT}'",
        reply_markup=get_reply_cancel_button(),
    )

    executor_id: int = callback_data.executor_id
    album_id: int = callback_data.album_id
    await state.update_data(executor_id=executor_id)
    await state.update_data(album_id=album_id)
    await state.set_state(FSMUpdateAlbumTitle.title)


@router.message(FSMUpdateAlbumTitle.title)
async def finish_update_album_title(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет заголовок альбома."""

    if message.text:
        await message.answer(
            text=messages.WAIT_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        album_id: int = data["album_id"]
        title: str = message.text.strip().lower()
        result_update_album_title: Result = await crud_service.update_album_tilte(
            executor_id=executor_id,
            album_id=album_id,
            title=title,
            logging_data=logging_data,
        )
        chat_id: int = message.chat.id

        await state.clear()
        if result_update_album_title.ok:
            await get_admin_panel(
                caption=result_update_album_title.data,
                chat_id=chat_id,
                bot=bot,
            )

        else:
            await get_admin_panel(
                caption=result_update_album_title.error.message,
                chat_id=chat_id,
                bot=bot,
            )
    else:
        await message.answer(
            text="Данные должны быть"
            " текстом\n\nВведите,снова, имя альбома"
            f" или нажмите '{messages.CANCEL_TEXT}'"
        )


# Обновление года альбома
class FSMUpdateAlbumYear(StatesGroup):
    """FSM для обновления года альбома."""

    executor_id: State = State()
    album_id: State = State()
    year: State = State()


@router.callback_query(StateFilter(None), AdminUpdateAlbumYearCallback.filter())
async def start_update_album_year(
    call: CallbackQuery,
    callback_data: AdminUpdateAlbumYearCallback,
    state: FSMContext,
):
    """Просит ввести год выпуска альбома."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        f"Введите год выпуска альбома или нажмите '{messages.CANCEL_TEXT}'",
        reply_markup=get_reply_cancel_button(),
    )

    executor_id: int = callback_data.executor_id
    album_id: int = callback_data.album_id
    await state.update_data(executor_id=executor_id)
    await state.update_data(album_id=album_id)
    await state.set_state(FSMUpdateAlbumYear.year)


@router.message(FSMUpdateAlbumYear.year)
async def finish_update_album_year(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет год выпуска альбома."""

    if message.text:
        result_year = check_number_is_positivity(number=message.text)
        if not result_year.ok:
            await message.answer(
                text=f"{result_year.error.message}\n\n"
                f"Введите снова год выпуска альбома или нажмите '{messages.CANCEL_TEXT}'"
            )
            return

        await message.answer(
            text=messages.WAIT_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        album_id: int = data["album_id"]
        year: int = result_year.data
        chat_id: int = message.chat.id

        result_update_executor_year: Result = await crud_service.update_album_year(
            executor_id=executor_id,
            album_id=album_id,
            year=year,
            logging_data=logging_data,
        )
        await state.clear()
        if result_update_executor_year.ok:
            await get_admin_panel(
                caption=result_update_executor_year.data,
                chat_id=chat_id,
                bot=bot,
            )
        else:
            await get_admin_panel(
                caption=result_update_executor_year.error.message,
                chat_id=chat_id,
                bot=bot,
            )
    else:
        await message.answer(
            text="Данные должны быть"
            " текстом\n\nВведите,снова, год выпуска альбома"
            f" или нажмите '{messages.CANCEL_TEXT}'"
        )


# Обновление жанров исполнителя
class FSMUpdateExecutorGenres(StatesGroup):
    """FSM для сценария обновления жанров исполнителя."""

    executor_id: State = State()
    genres: State = State()


@router.callback_query(StateFilter(None), AdminUpdateExecutorGenresCallback.filter())
async def start_update_executor_genres(
    call: CallbackQuery,
    callback_data: AdminUpdateExecutorGenresCallback,
    state: FSMContext,
):
    """Просит ввести жанры исполнителя."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        "Введите жанры исполнителя через точку\n\nПример: панк-рок.краст.треш-метал\n\n"
        f"Или нажмите '{messages.CANCEL_TEXT}'",
        reply_markup=get_reply_cancel_button(),
    )

    executor_id: int = callback_data.executor_id
    await state.update_data(executor_id=executor_id)
    await state.set_state(FSMUpdateExecutorGenres.genres)


@router.message(FSMUpdateExecutorGenres.genres)
async def finish_update_executor_genres(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет жанры исполнителя."""
    if message.text:
        await message.answer(
            text=messages.WAIT_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        genres: List[str] = message.text.split(".")

        result_update_executor_genres = await crud_service.update_executor_genres(
            executor_id=executor_id, genres=genres, logging_data=logging_data
        )
        chat_id: int = message.chat.id

        await state.clear()
        if result_update_executor_genres.ok:
            await get_admin_panel(
                caption=result_update_executor_genres.data,
                chat_id=chat_id,
                bot=bot,
            )
        else:
            await get_admin_panel(
                caption=result_update_executor_genres.error.message,
                chat_id=chat_id,
                bot=bot,
            )
    else:
        await message.answer(
            text="Данные должны быть"
            " текстом\n\nВведите,снова, год выпуска альбома"
            f" или нажмите '{messages.CANCEL_TEXT}'"
        )
