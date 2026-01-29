from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters.state import StateFilter

from core.response.messages import messages
from app.bot.db.uow import UnitOfWork
from app.bot.db.response import SongResponse
from app.bot.db.db_helper import db_helper


router: Router = Router(name="main")


@router.message(
    StateFilter(None),
    F.text,
)
async def main(
    message: Message,
    bot: Bot,
    get_main_keyboards,
) -> None:
    """Отправляет пользователю reply клавиатуру главного меню."""
    async with UnitOfWork() as uow:
        user = await uow.users.create_user(
            name=message.from_user.first_name,
            telegram=message.chat.id,
        )
        user = await uow.users.get_user_by_telegram(telegram=message.chat.id)
        genres = await uow.genres.get_or_create_genres(titles=["punk", "horror punk"])
        executor = await uow.executors.create_executor(
            name="Король и шут", country="Russia", user=user, genres=genres
        )
        album = await uow.albums.create_album(
            executor=executor, title="Жаль нет ружья", year=2002
        )
        songs = await uow.songs.create_songs(
            album=album,
            song_repsonse=[
                SongResponse(file_id="ddasdsad", title="песня 1"),
                SongResponse(file_id="dsadasdsads", title="песня 2"),
                SongResponse(file_id="dsadыввdsads", title="песня 3")
            ],
        )
        await uow.session.commit()


    # Удаляет сообщение которое было последним
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    await message.answer(
        text=str("ok"),
        reply_markup=get_main_keyboards,
    )
