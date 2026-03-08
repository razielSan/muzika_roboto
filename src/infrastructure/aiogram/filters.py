from typing import Optional

from aiogram.filters.callback_data import CallbackData


class BackMenuUserPanel(CallbackData, prefix="back_menu_user_panel"):
    pass


class PlaySongsCollectionSongs(CallbackData, prefix="play_songs_collection_songs"):
    song_id: int


class ShowAlbumExecutor(CallbackData, prefix="show_album_executor"):
    album_id: int
    user_id: Optional[int]
    executor_id: int
    current_page_executor: int


class AddCallbackDataFilters:
    class SongCollectionSongs(CallbackData, prefix="add_collection_song"):
        pass


class ScrollingCallbackDataFilters:
    class SongCollectionSongs(CallbackData, prefix="scrolling_collection_song"):
        position: int
        offset: int

    class DeleteMenuSongColletionSongs(
        CallbackData, prefix="delete_menu_scrolling_collection_songs"
    ):
        position: int
        offset: int

    class AlbumsExecutorGlobalLibrary(
        CallbackData, prefix="albums_executor_scrolling_global_library"
    ):
        executor_id: int
        user_id: Optional[int]
        current_page_executor: int
        position: int
        offset: int

    class ExecutorPageGlobalLibrary(
        CallbackData, prefix="executor_scrolling_global_library"
    ):
        executor_id: int
        user_id: Optional[int]
        current_page_executor: int


class UpdateCallbackDataFilters:
    class SongTitleCollectionSongs(CallbackData, prefix="update_tilte_song_collection"):
        pass

    class UserCollectionSongsPhotoFileId(
        CallbackData, prefix="update_Аuser_collection_songs_file_id"
    ):
        pass


class DeleteCallbackDataFilters:
    class SongCollectionSongs(CallbackData, prefix="delete_songs_collection_songs"):
        pass

    class ButtonsDeleteSongColletionSongs(
        CallbackData, prefix="delete_buttons_song_collection_songs"
    ):
        """Фильтр для размечивания песен как на готовые к удалению."""

        song_id: int
        position: int

    class ConfirmDeleteSongCollectionSongs(
        CallbackData, prefix="confirm_delete_songs_collection_songs"
    ):
        """Подтверждение на удаление песен."""

        pass

    class CompleteDeleteSongCollectionSongs(
        CallbackData, prefix="complete_del_songs_coll_songs"
    ):
        """Cценарий удаления песен."""

        pass
