from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from infrastructure.aiogram.filters import AddCallbackDataFilters
from core.response.messages import messages


router = Router(name=__name__)


class FSMAddSongCollection(StatesGroup):
    unique_songs_titles: State = State()
    songs: State = State()


@router.callback_query(
    StateFilter(None), AddCallbackDataFilters.CollectionSong.filter()
)
async def add_collection_song(
    call: CallbackQuery, callback_data: AddCallbackDataFilters.CollectionSong
):

    await call.message.edit_reply_markup(reply_markup=None)
    
    await call.message.answer(text="Скидывайте песня для добавления в сборник\n\n")
