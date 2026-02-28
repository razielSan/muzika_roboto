from aiogram.filters.callback_data import CallbackData


class AddCallbackDataFilters:
    class SongCollectionSong(CallbackData, prefix="add_collection_song"):
        pass


class ScrollingCallbackDataFilters:
    class SongCollectionSong(CallbackData, prefix="scrolling_collection_song"):
        position: int
        offset: int


class UpdateCallbackDataFilters:
    class SongTitleCollectionSong(CallbackData, prefix="update_tilte_song_collection"):
        pass
