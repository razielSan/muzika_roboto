from aiogram.filters.callback_data import CallbackData


class AddCallbackDataFilters:
    class CollectionSong(CallbackData, prefix="add_collection_song"):
        pass
