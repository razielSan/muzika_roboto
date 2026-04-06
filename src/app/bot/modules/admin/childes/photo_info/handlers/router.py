from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.admin.childes.photo_info.settings import settings
from app.bot.modules.admin.settings import settings as admin_settings
from app.bot.modules.admin.response import get_keyboards_menu_buttons
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.aiogram.messages import user_messages
from infrastructure.db.utils.editing import get_info_photo


router: Router = Router(name=__name__)


class FSMPhotoInfo(StatesGroup):
    """FSM для модуля photo_info."""

    file_id: State = State()


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def photo_info(call: CallbackQuery, state: FSMContext):
    """Просит пользователя скинуть фото."""

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        text=f"Скидывайте фото для получения file_id\n\n"
        f"{user_messages.CLICK_CANCEL_BUTTON.format(button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value)}",
        reply_markup=get_reply_cancel_button(
            cancel_button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value
        ),
    )

    await state.set_state(FSMPhotoInfo.file_id)


@router.message(FSMPhotoInfo.file_id, F.photo)
async def get_photo_file_id(message: Message, state: FSMContext, bot: Bot) -> None:
    """Скидывает пользователю file_id и file_unique_id изображения."""

    await state.clear()

    file_id: str = message.photo[-1].file_id
    file_unique_id: str = message.photo[-1].file_unique_id
    data_photo: str = get_info_photo(file_id=file_id, file_unique_id=file_unique_id)

    await message.answer(
        text=data_photo,
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=user_messages.ADMIN_PANEL_CAPTION,
        reply_markup=get_keyboards_menu_buttons,
        photo=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
    )
    return


@router.message(FSMPhotoInfo.file_id)
async def get_photo_file_id_message(message: Message) -> None:
    # Если пользователь скинул не фото
    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="фото")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value
        )
    )
