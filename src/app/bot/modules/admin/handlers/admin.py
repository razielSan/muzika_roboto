from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from app.bot.modules.admin.response import get_keyboards_menu_buttons
from app.bot.modules.admin.settings import settings
from app.bot.modules.admin.filters import AdminFilter, BackAdminMenuCallback
from app.bot.utils.delete import delete_previous_message
from core.response.messages import messages


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
        text=messages.ADMIN_PANEL_TEXT,
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=messages.ADMIN_PANEL_TEXT,
        reply_markup=get_keyboards_menu_buttons,
        photo=settings.ADMIN_PANEL_PHOTO_FILE_ID,
    )


@router.callback_query(StateFilter(None), BackAdminMenuCallback.filter())
async def base_music(
    call: CallbackQuery,
    callback_data: BackAdminMenuCallback,
) -> None:
    """Возвращает к главному меню админки по нажатию кнопки."""

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=settings.ADMIN_PANEL_PHOTO_FILE_ID,
            caption=messages.ADMIN_PANEL_TEXT,
        ),
        reply_markup=get_keyboards_menu_buttons,
    )


@router.message(F.text == messages.CANCEL_TEXT)
async def admin_cancel_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
) -> None:
    """Отменяет все действия."""

    current_state = await state.get_state()
    if not current_state:
        return

    await state.clear()

    await message.answer(
        text=f"{messages.CANCEL_MESSAGE}\n\nВозвращение к админ панели",
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=messages.ADMIN_PANEL_TEXT,
        reply_markup=get_keyboards_menu_buttons,
        photo=settings.ADMIN_PANEL_PHOTO_FILE_ID,
    )
