from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.settings import settings as bot_settings
from app.bot.modules.music_library.utils.music_library import (
    callback_update_menu_inline_music_library,
)
from app.bot.services.music_library.show_executor_page import (
    ShowExecutorPageCallbackService,
)
from application.use_cases.db.music_library.sync_executor import SyncExecutorLibrary
from application.use_cases.db.music_library.desync_executor import DesyncExecutorLibrary
from infrastructure.aiogram.filters import SyncExecutor, DesyncExecutor
from infrastructure.db.uow import UnitOfWork
from infrastructure.db.utils.editing import get_information_executor
from infrastructure.aiogram.messages import resolve_message, user_messages, LIMIT_ALBUMS
from core.logging.api import get_loggers
from core.response.response_data import LoggingData


router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), SyncExecutor.filter())
async def sync_executor(
    call: CallbackQuery,
    callback_data: SyncExecutor,
    user,
):
    user_id = user.id
    executor_id = callback_data.executor_id
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result_sync = await SyncExecutorLibrary(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(executor_id=executor_id, user_id=user_id)

    if result_sync.ok:
        success_message = resolve_message(code=result_sync.code)
        await call.answer(text=success_message)

    if not result_sync.ok:
        error_message = resolve_message(code=result_sync.error.code)
        await call.answer(text=error_message)


@router.callback_query(StateFilter(None), DesyncExecutor.filter())
async def desync_executor(
    call: CallbackQuery,
    callback_data: DesyncExecutor,
    user,
):
    user_id = user.id
    executor_id = callback_data.executor_id
    logging_data = get_loggers(name=music_library_settings.NAME_FOR_LOG_FOLDER)

    result_desync_executor = await DesyncExecutorLibrary(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(executor_id=executor_id, user_id=user_id)

    if result_desync_executor.ok:
        if (
            result_desync_executor.empty
        ):  # если после десинхронизации в библиотеке нет исполнителей
            not_found_message = resolve_message(code=result_desync_executor.code)
            await call.answer(text=not_found_message)
            await callback_update_menu_inline_music_library(
                call=call, caption=user_messages.USER_PANEL_CAPTION
            )
            return

        success_message = resolve_message(code=result_desync_executor.code)
        await call.answer(text=success_message)
        await ShowExecutorPageCallbackService(
            uow=UnitOfWork(),
            logging_data=logging_data,
            call=call,
        ).execute(
            user_id=user_id,
            get_information_executor=get_information_executor,
            limit_albums=LIMIT_ALBUMS,
            album_position=0,
            current_page=1,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        )
        return
    else:
        error_message = resolve_message(code=result_desync_executor.error.code)
        await call.answer(text=error_message)
