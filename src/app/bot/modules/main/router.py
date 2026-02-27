from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter

from app.bot.modules.main.settings import settings
from core.logging.api import get_loggers
from application.use_cases.db.get_or_create_user import GetOrCreateUser
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.messages import ERRORS
from domain.errors.error_code import ErorrCode
from infrastructure.aiogram.messages import user_messages


router: Router = Router(name="main")


@router.message(
    StateFilter(None),
    F.text == "/start",
)
async def main(
    message: Message,
    bot: Bot,
) -> None:
    """Отправляет пользователю reply клавиатуру главного меню."""

    name: str = message.from_user.first_name
    telegram: int = message.from_user.id
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result = await GetOrCreateUser(uow=UnitOfWork(), logging_data=logging_data).execute(
        name=name,
        telegram=telegram,
    )
    if not result.ok:
        if result.error.code == ErorrCode.UNKNOWN_ERROR.name:
            await message.answer(
                text=f"{ERRORS[result.error.code]}\n\n{user_messages.TRY_PRESSING_START_AGAIN}"
            )
        return

    # Удаляет сообщение которое было последним
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    await message.answer(
        text=f"☕ Будь как дома, {name}",
        reply_markup=ReplyKeyboardRemove(),
    )
