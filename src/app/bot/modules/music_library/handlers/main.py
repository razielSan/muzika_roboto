from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext


from app.bot.modules.music_library.settings import settings
from app.bot.modules.music_library.response import get_keyboards_menu_buttons
from app.bot.utils.delete import delete_previous_message
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.aiogram.messages import user_messages
from core.response.messages import messages


router = Router(name=settings.SERVICE_NAME)


@router.message(StateFilter(None), F.text == f"/{settings.SERVICE_NAME}")
async def menu_music_library(message: Message, bot: Bot):

    await delete_previous_message(bot=bot, message=message)

    chat_id: int = message.chat.id

    await message.answer(
        text=user_messages.MAIN_MENU,
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=chat_id,
        photo=settings.MENU_IMAGE_FILE_ID,
        caption=settings.MENU_CALLBACK_TEXT,
        reply_markup=get_keyboards_menu_buttons,
    )


@router.message(F.text == user_messages.USER_CANCEL_TEXT)
async def music_library_cancel_handler(
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
        text=f"{messages.CANCEL_MESSAGE}\n\n{user_messages.MAIN_MENU}",
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=settings.MENU_CALLBACK_TEXT,
        reply_markup=get_keyboards_menu_buttons,
        photo=settings.MENU_IMAGE_FILE_ID,
    )
