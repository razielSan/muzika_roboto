from aiogram.filters.callback_data import CallbackData


class AddCallbackDataFilters:
    class CollectionSong(CallbackData, prefix="add_collection_song"):
        pass


class ScrollingCallbackDataFilters:
    class CollectionSong(CallbackData, prefix="scrolling_collection_song"):
        position: int
        offset: int
