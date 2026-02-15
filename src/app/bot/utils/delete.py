from aiogram import Bot
from aiogram.types import Message


async def delete_previous_message(bot: Bot, message: Message):
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass
