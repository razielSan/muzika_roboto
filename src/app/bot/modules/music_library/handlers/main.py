from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters.state import StateFilter


from app.bot.modules.music_library.settings import settings
from app.bot.modules.music_library.response import get_keyboards_menu_buttons
from app.bot.utils.delete import delete_previous_message


router = Router(name=settings.SERVICE_NAME)


@router.message(StateFilter(None), F.text == f"/{settings.SERVICE_NAME}")
async def menu_music_library(message: Message, bot: Bot):

    await delete_previous_message(bot=bot, message=message)

    chat_id: int = message.chat.id

    await bot.send_photo(
        chat_id=chat_id,
        photo=settings.MENU_IMAGE_FILE_ID,
        caption="📻 Моя Музыкальная Коллекция",
        reply_markup=get_keyboards_menu_buttons,
    )
