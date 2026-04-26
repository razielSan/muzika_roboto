from typing import Dict

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from app.bot.modules.admin.response import get_keyboards_menu_buttons
from app.bot.modules.admin.settings import settings
from app.bot.filters.admin_filters import AdminFilter
from app.bot.utils.delete import delete_previous_message
from infrastructure.aiogram.fsm.keys import FSMFlags
from infrastructure.aiogram.messages import user_messages
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.filters import BackAdminMenuCallback


router: Router = Router(name=__name__)


@router.message(
    AdminFilter(),
    StateFilter(None),
    F.text == f"/{settings.SERVICE_NAME}",
)
async def admin(
    message: Message,
    bot: Bot,
) -> None:
    """Возвращает главное меню админки."""

    await delete_previous_message(bot=bot, message=message)

    await bot.send_message(
        chat_id=message.chat.id,
        text=user_messages.MAIN_MENU,
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=user_messages.ADMIN_PANEL_CAPTION,
        reply_markup=get_keyboards_menu_buttons,
        photo=settings.ADMIN_PANEL_PHOTO_FILE_ID,
    )


@router.callback_query(BackAdminMenuCallback.filter())
async def back_admin_menu(
    call: CallbackQuery,
    callback_data: BackAdminMenuCallback,
    state: FSMContext,
) -> None:
    """Возвращает к главному меню админки по нажатию кнопки."""

    data: Dict = await state.get_data()
    search_executor: str = data.get(FSMFlags.SEARCH_EXECUTOR)
    if search_executor:  # для сценария поиска исполнителй, удаляет клавиатуру
        await call.message.answer(
            text=user_messages.MAIN_MENU, reply_markup=ReplyKeyboardRemove()
        )

    await state.clear()
    await call.message.edit_media(
        media=InputMediaPhoto(
            media=settings.ADMIN_PANEL_PHOTO_FILE_ID,
            caption=user_messages.ADMIN_PANEL_CAPTION,
        ),
        reply_markup=get_keyboards_menu_buttons,
    )


@router.message(F.text == KeyboardResponse.ADMIN_CANCEL_BUTTON.value)
async def admin_cancel_handelr(message: Message, state: FSMContext, bot: Bot):
    """Обработчик для кнопки отмены"""

    data: Dict = await state.get_data()

    processing: str = data.get(FSMFlags.PROCESSING)
    if (
        processing
    ):  # Для сценариев, когда во время обработки долгого запроса нажали кнопку отмена,
        # например скачивание исполнителя из пути
        return

    await state.clear()

    chat_id: int = message.chat.id

    await state.clear()
    await message.answer(
        text=user_messages.USER_CANCEL_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=chat_id,
        caption=user_messages.ADMIN_PANEL_CAPTION,
        reply_markup=get_keyboards_menu_buttons,
        photo=settings.ADMIN_PANEL_PHOTO_FILE_ID,
    )
