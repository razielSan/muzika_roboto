from typing import Dict, List

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.filters.admin_filters import (
    AdminUpdatePhotoExecutorCallback,
    AdminUpdatePhotoAlbumCallback,
    AdminUpdateExecutorNameCallback,
    AdminUpdateExecutorCountryCallback,
    AdminUpdateAlbumTitleCallback,
    AdminUpdateAlbumYearCallback,
    AdminUpdateExecutorGenresCallback,
    AdminUpdateSongTitleCallback,
)
from app.app_utils.keyboards import get_reply_cancel_button
from app.bot.utils.editing import get_info_executor, get_info_album
from core.response.messages import messages
from core.utils.chek import check_number_is_positivity
from app.bot.modules.admin.childes.base_music.services.crud import crud_service
from app.bot.modules.admin.childes.base_music.services.base_music import (
    base_music_service,
)
from app.bot.modules.admin.utils.admin import get_admin_panel
from app.bot.utils.delete import delete_previous_message
from core.response.response_data import Result
from infrastructure.aiogram.legacy_response import ServerDatabaseResponse
from infrastructure.aiogram.response import LIMIT_ALBUMS, LIMIT_SONGS
from app.bot.utils.navigator import (
    open_album_pages,
    open_album_pages_with_not_songs,
    open_executor_pages,
)


router: Router = Router(name=__name__)


# Обновление фото исполнителя
class FSMUpdatePhotoExecutor(StatesGroup):
    """FSM для сценария обновления фото исполнителя."""

    current_page_executor: State = State()
    count_pages_executor: State = State()
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
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    await call.message.answer(
        f"Скидывайте фото исполнителя\n\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )
    await state.update_data(executor_id=executor_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(count_pages_executor=count_pages_executor)
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

        executor_id: int = data["executor_id"]
        photo_file_id: str = message.photo[-1].file_id
        photo_file_unique_id: str = message.photo[-1].file_unique_id
        chat_id: int = message.chat.id
        current_page_executor = data.get("current_page_executor")
        count_pages_executor = data.get("count_pages_executor")

        result_update: Result = await crud_service.update_photo_executor(
            executor_id=executor_id,
            photo_file_id=photo_file_id,
            photo_file_unique_id=photo_file_unique_id,
        )

        await state.clear()
        if result_update.ok:  # перебрасываем на страницу исполнителя
            result: Result = await base_music_service.show_executor(
                get_info_executor=get_info_executor,
                page_executor=current_page_executor,
            )

            await message.answer(text=result_update.data)
            if result.ok:
                await open_executor_pages(
                    executor_response=result.data,
                    limit_albums=LIMIT_ALBUMS,
                    count_pages_executor=count_pages_executor,
                    current_page_executor=current_page_executor,
                    message=message,
                    bot=bot,
                    executor_id=executor_id,
                )

                return

            # Если произошла ошибка при возвращении на страницу исполнителя
            await get_admin_panel(
                chat_id=chat_id,
                caption=result.error.message,
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
            f" исполнителя\n{messages.CANCEL_TEXT}: Отмена",
            reply_markup=get_reply_cancel_button(),
        )


# Обновление фото альбома
class FSMUpdatePhotoAlmum(StatesGroup):
    """FSM для сценария обновления фото альбома."""

    current_page_executor: State = State()
    count_pages_executor: State = State()
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
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    await call.message.answer(
        f"Скидывайте фото альбома\n\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )
    await state.update_data(executor_id=executor_id)
    await state.update_data(album_id=album_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(count_pages_executor=count_pages_executor)
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

        data: Dict = await state.get_data()

        executor_id: int = data["executor_id"]
        album_id: int = data["album_id"]
        photo_file_id: str = message.photo[-1].file_id
        photo_file_unique_id: str = message.photo[-1].file_unique_id
        chat_id: int = message.chat.id
        current_page_executor: int = data.get("current_page_executor")
        count_pages_executor: int = data.get("count_pages_executor")

        result_update_photo_album: Result = await crud_service.update_album_photo(
            executor_id=executor_id,
            album_id=album_id,
            photo_file_id=photo_file_id,
            photo_file_unique_id=photo_file_unique_id,
        )
        await state.clear()
        if result_update_photo_album.ok:  # возвращаемся на страницу альбома
            result: Result = await base_music_service.show_songs_with_album(
                get_info_album=get_info_album,
                album_id=album_id,
                executor_id=executor_id,
            )
            await message.answer(text=result_update_photo_album.data)
            if result.ok and not result.empty:  # если есть песни в альбоме
                await open_album_pages(
                    songs=result.data,
                    message=message,
                    limit_songs=LIMIT_SONGS,
                    executor_id=executor_id,
                    count_pages_executor=count_pages_executor,
                    current_page_executor=current_page_executor,
                    bot=bot,
                    album_id=album_id,
                )
                return

            if result.ok and result.empty:  # Если на странице нет песен
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

            if not result.ok:
                await get_admin_panel(
                    caption=result.error.message,
                    chat_id=chat_id,
                    bot=bot,
                )
                return
        else:  # если произошла ошибка при возвращении к альбому
            await get_admin_panel(
                chat_id=chat_id,
                caption=result_update_photo_album.error.message,
                bot=bot,
            )

    else:
        await message.answer(
            text="Данные должны быть"
            " изображением\n\nСкидывайте,снова, фото"
            f" альбома\n{messages.CANCEL_TEXT}: Отмена",
            reply_markup=get_reply_cancel_button(),
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
    """Просит ввести имя исполнителя."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        f"Введите имя исполнителя\n\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )

    executor_id: int = callback_data.executor_id
    await state.update_data(executor_id=executor_id)
    await state.set_state(FSMUpdateExecutorName.name)


@router.message(FSMUpdateExecutorName.name)
async def finish_update_executor_name(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет имя исполнителя."""

    if message.text:
        await message.answer(
            text=messages.WAIT_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        name: str = message.text.strip().lower()

        chat_id: int = message.chat.id

        result_update_executor_name: Result = await crud_service.update_executor_name(
            executor_id=executor_id,
            name=name,
        )
        await state.clear()
        if result_update_executor_name.ok:
            await get_admin_panel(
                caption=result_update_executor_name.data,
                chat_id=chat_id,
                bot=bot,
            )
            return

        # Если произошла ошибка при обновлении имени исполнителя
        await get_admin_panel(
            caption=result_update_executor_name.error.message,
            chat_id=chat_id,
            bot=bot,
        )

    else:
        await message.answer(
            text="Данные должны быть"
            " текстом\n\nВведите,снова, имя исполнителя"
            f"\n{messages.CANCEL_TEXT}: Отмена"
        )


# Обновление страны исполнителя
class FSMUpdateExecutorCountry(StatesGroup):
    """FSM для сценария обновления страны исполнителя."""

    current_page_executor: State = State()
    count_pages_executor: State = State()
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

    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    await call.message.answer(
        f"Введите страну исполнителя\n\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )

    executor_id: int = callback_data.executor_id
    await state.update_data(executor_id=executor_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(count_pages_executor=count_pages_executor)
    await state.set_state(FSMUpdateExecutorCountry.country)


@router.message(FSMUpdateExecutorCountry.country)
async def finish_update_executor_country(message: Message, state: FSMContext, bot: Bot):
    """Обновляет страну исполнителя."""
    if message.text:
        await message.answer(
            text=messages.WAIT_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        country: str = message.text.strip().lower()
        chat_id: int = message.chat.id
        current_page_executor: int = data.get("current_page_executor")
        count_pages_executor: int = data.get("count_pages_executor")

        result_update_executor_country: Result = (
            await crud_service.update_executor_country(
                executor_id=executor_id,
                country=country,
            )
        )

        await state.clear()
        if result_update_executor_country.ok:  # возвращаемся обратно к исполнителю
            result: Result = await base_music_service.show_executor(
                get_info_executor=get_info_executor,
                page_executor=current_page_executor,
            )
            await message.answer(text=result_update_executor_country.data)
            if result.ok:
                await open_executor_pages(
                    executor_response=result.data,
                    limit_albums=LIMIT_ALBUMS,
                    count_pages_executor=count_pages_executor,
                    current_page_executor=current_page_executor,
                    message=message,
                    bot=bot,
                    executor_id=executor_id,
                )

                return
            # Если произошла ошибка при возвращении к исполнителю
            await get_admin_panel(
                caption=result.error.message,
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
            " текстом\n\nВведите,снова, страну исполнителя\n"
            f"{messages.CANCEL_TEXT}: Отмена"
        )


# Обновление заголовок альбома
class FSMUpdateAlbumTitle(StatesGroup):
    """ "FSM для обновления заголовка альбома."""

    count_pages_executor: State = State()
    current_page_executor: State = State()
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

    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    await call.message.answer(
        f"Введите название альбома\n\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )

    executor_id: int = callback_data.executor_id
    album_id: int = callback_data.album_id
    await state.update_data(executor_id=executor_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(count_pages_executor=count_pages_executor)
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

        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        album_id: int = data["album_id"]
        title: str = message.text.strip().lower()
        current_page_executor: int = data.get("current_page_executor")
        count_pages_executor: int = data.get("count_pages_executor")

        result_update_album_title: Result = await crud_service.update_album_tilte(
            executor_id=executor_id,
            album_id=album_id,
            title=title,
        )
        chat_id: int = message.chat.id

        await state.clear()
        if result_update_album_title.ok:  # возвращение на страницу альбома
            result: Result = await base_music_service.show_songs_with_album(
                get_info_album=get_info_album,
                album_id=album_id,
                executor_id=executor_id,
            )
            await message.answer(text=result_update_album_title.data)
            if result.ok and not result.empty:  # если есть песни на странице
                await open_album_pages(
                    songs=result.data,
                    message=message,
                    limit_songs=LIMIT_SONGS,
                    executor_id=executor_id,
                    count_pages_executor=count_pages_executor,
                    current_page_executor=current_page_executor,
                    bot=bot,
                    album_id=album_id,
                )
                return

            if result.ok and result.empty:  # Если на странице нет песен
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
                    chat_id=chat_id,
                    bot=bot,
                )
                return

        else:  # Если произошла ошибка при возвращении к альбому
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

    count_pages_executor: State = State()
    current_page_executor: State = State()
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
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    await call.message.answer(
        f"Введите год выпуска альбома\n\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )

    executor_id: int = callback_data.executor_id
    album_id: int = callback_data.album_id
    await state.update_data(executor_id=executor_id)
    await state.update_data(album_id=album_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(count_pages_executor=count_pages_executor)
    await state.set_state(FSMUpdateAlbumYear.year)


@router.message(FSMUpdateAlbumYear.year)
async def finish_update_album_year(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет год выпуска альбома."""

    if message.text:
        result_year: Result = check_number_is_positivity(number=message.text)
        if not result_year.ok:
            await message.answer(
                text=f"{result_year.error.message}\n\n"
                f"Введите,снова, год выпуска альбома\n{messages.CANCEL_TEXT}: Отмена"
            )
            return

        await message.answer(
            text=messages.WAIT_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        album_id: int = data["album_id"]
        year: int = result_year.data
        chat_id: int = message.chat.id
        current_page_executor: int = data.get("current_page_executor")
        count_pages_executor: int = data.get("count_pages_executor")
        result_update_album_year: Result = await crud_service.update_album_year(
            executor_id=executor_id,
            album_id=album_id,
            year=year,
        )
        await state.clear()
        if result_update_album_year.ok:  # Возвращает назад к альбомам

            result: Result = await base_music_service.show_songs_with_album(
                get_info_album=get_info_album,
                album_id=album_id,
                executor_id=executor_id,
            )
            await message.answer(text=result_update_album_year.data)

            if result.ok and not result.empty:  # если есть песни в альбоме
                await open_album_pages(
                    songs=result.data,
                    message=message,
                    limit_songs=LIMIT_SONGS,
                    executor_id=executor_id,
                    count_pages_executor=count_pages_executor,
                    current_page_executor=current_page_executor,
                    bot=bot,
                    album_id=album_id,
                )
                return

            if result.ok and result.empty:  # Если на странице нет песен
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
            if not result.ok:
                await get_admin_panel(
                    caption=result.error.message,
                    chat_id=chat_id,
                    bot=bot,
                )
                return

        else:  # если произошла ошибка при возвращении к альбомам
            await get_admin_panel(
                caption=result_update_album_year.error.message,
                chat_id=chat_id,
                bot=bot,
            )
    else:
        await message.answer(
            text="Данные должны быть"
            " текстом\n\nВведите,снова, год выпуска альбома"
            f"\n{messages.CANCEL_TEXT}: Отмена"
        )


# Обновление жанров исполнителя
class FSMUpdateExecutorGenres(StatesGroup):
    """FSM для сценария обновления жанров исполнителя."""

    executor_id: State = State()
    genres: State = State()
    current_page_executor: State = State()
    count_pages_executor: State = State()


@router.callback_query(StateFilter(None), AdminUpdateExecutorGenresCallback.filter())
async def start_update_executor_genres(
    call: CallbackQuery,
    callback_data: AdminUpdateExecutorGenresCallback,
    state: FSMContext,
):
    """Просит ввести жанры исполнителя."""

    await call.message.edit_reply_markup(reply_markup=None)

    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor
    executor_id: int = callback_data.executor_id
    await state.update_data(executor_id=executor_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(count_pages_executor=count_pages_executor)
    await state.set_state(FSMUpdateExecutorGenres.genres)

    await call.message.answer(
        "Введите жанры исполнителя через точку\n\nПример: панк-рок.краст.треш-метал"
        f"\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )


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

        data: Dict = await state.get_data()
        executor_id: int = data["executor_id"]
        genres: List[str] = message.text.split(".")
        current_page_executor: int = data.get("current_page_executor")
        count_pages_executor: int = data.get("count_pages_executor")

        result_update_executor_genres: Result = (
            await crud_service.update_executor_genres(
                executor_id=executor_id,
                genres=genres,
            )
        )
        chat_id: int = message.chat.id

        await state.clear()
        if result_update_executor_genres.ok:  # возвращаемся к исполнителю

            result: Result = await base_music_service.show_executor(
                get_info_executor=get_info_executor,
                page_executor=current_page_executor,
            )
            await message.answer(text=result_update_executor_genres.data)
            if result.ok:

                await open_executor_pages(
                    executor_response=result.data,
                    limit_albums=LIMIT_ALBUMS,
                    count_pages_executor=count_pages_executor,
                    current_page_executor=current_page_executor,
                    message=message,
                    bot=bot,
                    executor_id=executor_id,
                )

                return
            # Если произошла ошибка при возвращении к исполнителю
            await get_admin_panel(
                caption=result.error.message,
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
            " текстом\n\nВведите,снова,жанры исполнителя\n"
            "Пример: панк-рок.краст.треш-метал\n"
            f"{messages.CANCEL_TEXT}: Отмена"
        )


# Обновление название песни
class FSMUpdateSongTitle(StatesGroup):
    """FSM для сценария обновления имени песни."""

    position: State = State()
    title: State = State()
    album_id: State = State()
    executor_id: State = State()
    current_page_executor: State = State()
    count_pages_executor: State = State()


@router.callback_query(StateFilter(None), AdminUpdateSongTitleCallback.filter())
async def start_update_title_song(
    call: CallbackQuery,
    callback_data: AdminUpdateSongTitleCallback,
    state: FSMContext,
):
    """Просит ввести имя песни для обновления."""

    await call.message.edit_reply_markup(reply_markup=None)

    executor_id: int = callback_data.executor_id
    album_id: int = callback_data.album_id
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    await state.update_data(album_id=album_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(count_pages_executor=count_pages_executor)
    await state.update_data(executor_id=executor_id)
    await state.set_state(FSMUpdateSongTitle.title)

    await call.message.answer(
        text=f"Введите название песни\n\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateSongTitle.title, F.text)
async def add_song_title(message: Message, state: FSMContext):
    """Просит ввести позицию песни."""

    title: str = message.text
    await state.update_data(title=title)
    await state.set_state(FSMUpdateSongTitle.position)

    await message.answer(
        text=f"Введите позицию песни\n\n{messages.CANCEL_TEXT}: Отмена"
    )


@router.message(FSMUpdateSongTitle.title)
async def add_song_title_message(message: Message, state: FSMContext):
    """Отправляет сообщение если были отправлены не те данные"""
    await message.answer(
        text=f"Данные должны быть в формате текст\n\n"
        f"Введите,снова, имя песни\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateSongTitle.position, F.text)
async def finish_add_song_title(message: Message, state: FSMContext, bot: Bot):
    """Обновляет имя песни."""

    data: dict = await state.get_data()

    chat_id: int = message.chat.id

    album_id: int = data.get("album_id")
    title: str = data.get("title")
    executor_id: int = data.get("executor_id")
    current_page_executor: int = data.get("current_page_executor")
    count_pages_executor: int = data.get("count_pages_executor")

    position_result: Result = check_number_is_positivity(number=message.text)
    if not position_result.ok:  # если данные не явлются положительным числом
        await message.answer(
            text=f"{position_result.error.message}\n\nВведите,снова,позицию песни",
            reply_markup=get_reply_cancel_button(),
        )
        return

    await message.answer(
        text=messages.WAIT_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )

    position: int = position_result.data

    result_update_song_title: Result = await crud_service.update_title_song(
        album_id=album_id,
        position=position,
        title=title,
    )
    if (
        result_update_song_title.ok and not result_update_song_title.empty
    ):  # если имя песни изменено
        result: Result = await base_music_service.show_songs_with_album(
            get_info_album=get_info_album,
            album_id=album_id,
            executor_id=executor_id,
        )
        await message.answer(
            text=result_update_song_title.data,
        )

        await state.clear()
        if result.ok and not result.empty:  # возвращение на страницу альбома
            await open_album_pages(
                songs=result.data,
                message=message,
                limit_songs=LIMIT_SONGS,
                executor_id=executor_id,
                count_pages_executor=count_pages_executor,
                current_page_executor=current_page_executor,
                bot=bot,
                album_id=album_id,
            )
            return

        if result.ok and result.empty:  # Если на странице нет песен
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
        if not result.ok:  # если произошла ошибка при возвращении к альбому
            msg: str = result.error.message
            await get_admin_panel(
                caption=result.error.message,
                chat_id=chat_id,
                bot=bot,
            )
            return

    if (
        result_update_song_title.ok and result_update_song_title.empty
    ):  # если нет песни с введенной позицией
        msg: str = result_update_song_title.data
        await message.answer(
            text=f"{msg}\n\nВведите,снова,позицию песни\n{messages.CANCEL_TEXT}: Отмена",
            reply_markup=get_reply_cancel_button(),
        )
        return
    if (
        not result_update_song_title.ok
    ):  # если произошла ошибка при изменении имени песни
        await state.clear()
        msg: str = result_update_song_title.error.message
        await get_admin_panel(
            caption=msg,
            chat_id=chat_id,
            bot=bot,
        )


@router.message(FSMUpdateSongTitle.position)
async def finish_add_song_title_message(message: Message, state: FSMContext):
    """Отправляет сообщение если были отправлены не те данные"""
    await message.answer(
        text=f"Данные должны быть в формате текст\n\n"
        f"Введите,снова,позицию песни\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )
