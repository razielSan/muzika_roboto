from aiogram import Bot, Dispatcher
from app.bot.settings import settings

telegram_bot: Bot = Bot(token=settings.TOKEN)
dp: Dispatcher = Dispatcher()
