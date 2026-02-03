from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters.state import StateFilter

from app.bot.modules.main.settings import settings


router: Router = Router(name="main")


@router.message(
    StateFilter(None),
    F.text == "/start",
)
async def main(
    message: Message,
    bot: Bot,
    get_main_inline_keyboards,
) -> None:
    """Отправляет пользователю reply клавиатуру главного меню."""

    # Удаляет сообщение которое было последним
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=settings.MENU_IMAGE_FILE_ID,
        reply_markup=get_main_inline_keyboards,
    )
