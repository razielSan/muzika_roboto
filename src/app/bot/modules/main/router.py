from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
from aiogram.filters.state import StateFilter

from app.bot.db.response import SongResponse
from app.bot.db.uow import UnitOfWork


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

    print(111)
    # path = Path("D:/Media\Music/8-bit/Broken Board Broken Life (Иркутск)")
    path = Path("D:/ProgrammingProjects/Python/Bot/Project/BOT_PROJECT/my_bot/Muzika Roboto/src/app/bot/modules/main/1.jpg")
    # for album in path.iterdir():
    #     position = 0
    #     array_song = []
    #     album_year, album_name = album.stem.split(")")
    #     album_year = int(album_year.strip("("))
    #     album_name = album_name.strip(" ()")
    #     for data in album.glob("*.MP3"):
    #         print("ok")
    #         position += 1
    #         msg = await bot.send_audio(
    #             chat_id=message.chat.id,
    #             audio=FSInputFile(path=data),
    #             title=data.stem,
    #             request_timeout=180,
    #         )
    #         array_song.append(
    #             SongResponse(
    #                 file_id=msg.audio.file_id,
    #                 title=data.stem,
    #                 file_unique_id=msg.audio.file_unique_id,
    #                 position=position,
    #             )
    #         )

    #     async with UnitOfWork() as uow:
    #         user = await uow.users.create_user(
    #             name=message.from_user.first_name,
    #             telegram=message.chat.id,
    #         )
    #         genres = await uow.genres.get_or_create_genres(titles=["8 бит"])
    #         executor = await uow.executors.create_executor(
    #             name="Broken Board Broken Life",
    #             country="Иркутск",
    #             user=user,
    #             genres=genres,
    #         )
    #         album = await uow.albums.create_album(
    #             executor=executor, title=album_name, year=album_year
    #         )

    #         songs = await uow.songs.create_songs(
    #             song_repsonse=array_song,
    #             album=album,
    #         )

    # await message.answer(
    #     text=str("ok"),
    #     reply_markup=get_main_inline_keyboards,
    # )
    print(1)
    msg = await bot.send_photo(
        chat_id=message.chat.id,
        photo=FSInputFile(path=path),
        caption="Text",
        reply_markup=get_main_inline_keyboards, 
        request_timeout=180,
    )
