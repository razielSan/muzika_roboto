from typing import Optional

from aiogram import Router
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter


from app.bot.settings import settings as bot_settings
from app.bot.modules.music_library.childes.user_library.settings import settings
from app.bot.helpers.executor import return_to_executor_page_callback
from app.bot.modules.music_library.utils.music_library import (
    callback_update_menu_inline_music_library,
)
from application.use_cases.db.music_library.delete_executor import DeleteExecutor
from application.use_cases.db.music_library.delete_album import DeleteAlbum
from infrastructure.aiogram.filters import DeleteCallbackDataFilters
from infrastructure.aiogram.messages import (
    user_messages,
    LIMIT_ALBUMS,
    resolve_message,
)
from infrastructure.aiogram.filters import DeleteCallbackDataFilters
from infrastructure.db.utils.editing import (
    get_information_executor,
)
from infrastructure.aiogram.keyboards.inline import (
    get_confirmation_delete_executor_button,
    get_confirmation_delete_album_buttons,
)
from infrastructure.db.uow import UnitOfWork
from core.logging.api import get_loggers
from core.response.response_data import Result, LoggingData

router: Router = Router(name=__name__)


# удаление исполнителя
@router.callback_query(
    StateFilter(None), DeleteCallbackDataFilters.ConfirmDeleteExecutor.filter()
)
async def delete_user_executor(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.ConfirmDeleteExecutor,
):
    """Просит подтвердить удаление исполнителя."""

    user_id: int = callback_data.user_id
    executor_id: int = callback_data.executor_id
    current_page_executor: int = callback_data.current_page_executor
    album_position: int = callback_data.album_position

    await call.message.edit_media(
        InputMediaPhoto(
            media=bot_settings.DELETE_IMAGE_FILE_ID,
            caption=user_messages.CAPTION_DELETE_EXECUTOR,
        ),
        reply_markup=get_confirmation_delete_executor_button(
            executor_id=executor_id,
            user_id=user_id,
            current_page_executor=current_page_executor,
            album_position=album_position,
        ),
    )


@router.callback_query(
    StateFilter(None), DeleteCallbackDataFilters.CompleteDeleteExecutor.filter()
)
async def confirm_delete_executor(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.CompleteDeleteExecutor,
):
    """Удаляет исполнителя."""

    executor_id: Optional[int] = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_delete_executor: Result = await DeleteExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(user_id=user_id, executor_id=executor_id)
    if result_delete_executor.ok:
        result_message: str = resolve_message(code=result_delete_executor.code)

        await return_to_executor_page_callback(
            user_id=user_id,
            uow=UnitOfWork,
            call=call,
            message=result_message,
            logging_data=logging_data,
            current_page_executor=1,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            limit_albums=LIMIT_ALBUMS,
            album_position=0,
            get_information_executor=get_information_executor,
        )

    if not result_delete_executor.ok:
        error_message: str = resolve_message(code=result_delete_executor.error.code)

        await call.answer(text=error_message)
        await callback_update_menu_inline_music_library(
            call=call,
            caption=user_messages.USER_PANEL_CAPTION,
        )


# удаление альбома


@router.callback_query(
    StateFilter(None), DeleteCallbackDataFilters.ConfirmDeleteAlbum.filter()
)
async def start_delete_album(
    call: CallbackQuery, callback_data: DeleteCallbackDataFilters.ConfirmDeleteAlbum
):
    """Просит подтвердить удаления альбома."""

    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    current_page_executor: int = callback_data.current_page_executor
    is_global_executor: bool = callback_data.is_global_executor
    album_id: int = callback_data.album_id
    album_position: int = callback_data.album_position

    await call.message.edit_media(
        InputMediaPhoto(
            media=bot_settings.DELETE_IMAGE_FILE_ID,
            caption=user_messages.CAPTION_DELETE_ALBUM,
        ),
        reply_markup=get_confirmation_delete_album_buttons(
            executor_id=executor_id,
            user_id=user_id,
            current_page_executor=current_page_executor,
            is_global_executor=is_global_executor,
            album_id=album_id,
            album_position=album_position,
        ),
    )


@router.callback_query(
    StateFilter(None), DeleteCallbackDataFilters.CompleteDeleteAlbum.filter()
)
async def end_delete_album(
    call: CallbackQuery, callback_data: DeleteCallbackDataFilters.CompleteDeleteAlbum
):
    """удаляет альбом."""

    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    current_page_executor: int = callback_data.current_page_executor
    album_id: int = callback_data.album_id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_delete_album: Result = await DeleteAlbum(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(executor_id=executor_id, album_id=album_id)
    if result_delete_album.ok:
        result_message: str = resolve_message(code=result_delete_album.code)

        await return_to_executor_page_callback(
            user_id=user_id,
            uow=UnitOfWork,
            call=call,
            message=result_message,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            limit_albums=LIMIT_ALBUMS,
            album_position=0,
            get_information_executor=get_information_executor,
        )

    if not result_delete_album.ok:
        error_message: str = resolve_message(code=result_delete_album.error.code)

        await call.answer(text=error_message)
        await callback_update_menu_inline_music_library(
            call=call,
            caption=user_messages.USER_PANEL_CAPTION,
        )
