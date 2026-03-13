from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.user_library.settings import settings
from app.bot.services.music_library.show_executor_page import ShowExecutorPageService
from app.bot.settings import settings as bot_settings
from application.use_cases.db.music_library.desync_executor import DesyncExecutorLibrary
from infrastructure.aiogram.messages import LIMIT_ALBUMS
from infrastructure.aiogram.filters import DesyncExecutor
from infrastructure.db.uow import UnitOfWork
from infrastructure.db.utils.editing import get_information_executor
from infrastructure.aiogram.messages import resolve_message
from core.logging.api import get_loggers

router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def user_library(
    call: CallbackQuery,
    user,
):
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    user_id = user.id

    await ShowExecutorPageService(
        uow=UnitOfWork,
        logging_data=logging_data,
        call=call,
    ).execute(
        get_information_executor=get_information_executor,
        user_id=user_id,
        limit_albums=LIMIT_ALBUMS,
        current_page=1,
        album_position=0,
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
    )


@router.callback_query(StateFilter(None), DesyncExecutor.filter())
async def desync_executor(
    call: CallbackQuery,
    callback_data: DesyncExecutor,
    user,
):
    user_id = user.id
    executor_id = callback_data.executor_id
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_desync_executor = await DesyncExecutorLibrary(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(executor_id=executor_id, user_id=user_id)

    if result_desync_executor.ok:
        if result_desync_executor.empty:
            not_found_message = resolve_message(code=result_desync_executor.code)
            await call.answer(text=not_found_message)
            return

        success_message = resolve_message(code=result_desync_executor.code)
        await call.answer(text=success_message)
        await ShowExecutorPageService(
            uow=UnitOfWork,
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
