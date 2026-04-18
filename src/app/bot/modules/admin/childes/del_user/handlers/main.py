from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.admin.childes.del_user.settings import settings
from app.bot.settings import settings as bot_settings
from app.bot.modules.admin.response import get_keyboards_menu_buttons
from application.process.del_user import process_delete_user
from domain.errors.error_code import ErorrCode
from infrastructure.db.db_helper import db_helper
from infrastructure.aiogram.messages import user_messages, resolve_message
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.db.uow import UnitOfWork
from core.logging.api import get_loggers
from core.response.response_data import LoggingData, Result


router = Router(name=__name__)


class FSMDeleteUser(StatesGroup):
    user_id: State = State()


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def del_user(call: CallbackQuery, state: FSMContext):
    """Просит ввести id пользователя для удаления."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=user_messages.ENTER_THE_USER_USER_ID,
        reply_markup=get_reply_cancel_button(
            cancel_button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value
        ),
    )
    await state.set_state(FSMDeleteUser.user_id)


@router.message(FSMDeleteUser.user_id, F.text)
async def finish_del_user(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Удаляет пользователя"""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    user_id: str = message.text

    result: Result = await process_delete_user(
        logging_data=logging_data,
        uwo=UnitOfWork(session_factory=db_helper.session),
        user_id=user_id,
    )
    if result.ok:
        await state.clear()
        result_message: str = resolve_message(code=result.code)

        await bot.send_message(
            chat_id=message.chat.id,
            text=result_message,
            reply_markup=ReplyKeyboardRemove(),
        )

        await bot.send_photo(
            chat_id=message.chat.id,
            caption=user_messages.ADMIN_PANEL_CAPTION,
            reply_markup=get_keyboards_menu_buttons,
            photo=bot_settings.ADMIN_PANEL_PHOTO_FILE_ID,
        )
    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        if result.error.code == ErorrCode.FAILED_CHECK_POSITIVITY.name:
            error_message = error_message.format(data="ID")

        await message.answer(
            text=f"{error_message}\n\n{user_messages.ENTER_THE_USER_USER_ID}"
        )


@router.message(FSMDeleteUser.user_id)
async def finish_del_user_message(
    message: Message,
):
    """Отправляет сообщение если были введены не те данные"""
    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
