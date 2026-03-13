from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter

from app.bot.modules.main.settings import settings
from application.use_cases.db.user.get_or_create_user import GetOrCreateUser
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.messages import resolve_message
from core.logging.api import get_loggers
from core.response.response_data import Result, LoggingData


router: Router = Router(name="main")


@router.message(
    StateFilter(None),
    F.text == "/start",
)
async def main(
    message: Message,
    bot: Bot,
) -> None:
    """Регестрирует пользователя."""

    name: str = message.from_user.first_name
    telegram: int = message.from_user.id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result: Result = await GetOrCreateUser(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        name=name,
        telegram=telegram,
    )
    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        await message.answer(text=error_message)
        return
    # Удаляет сообщение которое было последним
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    await message.answer(
        text=f"☕ Будь как дома, {name}\n\n☕ Музыкальная библиотека открыта",
        reply_markup=ReplyKeyboardRemove(),
    )
