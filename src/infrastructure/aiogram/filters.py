from typing import Optional

from aiogram.filters.callback_data import CallbackData


class BackMenuUserPanel(CallbackData, prefix="back_menu_u_p"):
    pass


class BackExecutorPage(CallbackData, prefix="back_exc_p"):
    user_id: Optional[int]
    album_position: int
    current_page: int


class PlaySongsAlbums(CallbackData, prefix="play_s_coll_s"):
    song_id: int
    album_id: int


class PlaySongsCollectionSongs(CallbackData, prefix="play_s_coll_s"):
    song_id: int


class ShowAlbumExecutor(CallbackData, prefix="show_al_ex"):
    album_position: int
    album_id: int
    user_id: Optional[int]
    executor_id: int
    current_page_executor: int


class SyncExecutor(CallbackData, prefix="sync_ex"):
    executor_id: int


class DesyncExecutor(CallbackData, prefix="desync_ex"):
    executor_id: int


class AddCallbackDataFilters:
    class SongCollectionSongs(CallbackData, prefix="add_coll_s"):
        pass


class ScrollingCallbackDataFilters:
    class SongCollectionSongs(CallbackData, prefix="scr_s_coll_s"):
        position: int
        offset: int

    class DeleteMenuSongColletionSongs(CallbackData, prefix="scr_del_menu_coll_s"):
        """Фильтря для пролистывания песен в меню удаления песен."""

        position: int
        offset: int

    class SongsAlbumGlobalLibrary(CallbackData, prefix="scr_s_al_gl_lib"):
        user_id: Optional[int]
        position: int
        offset: int
        executor_id: int
        current_page_executor: int
        album_id: int

    class AlbumsExecutorGlobalLibrary(CallbackData, prefix="scr_al_ex_gl_lib"):
        executor_id: int
        user_id: Optional[int]
        current_page_executor: int
        position: int
        offset: int

    class ExecutorPageGlobalLibrary(CallbackData, prefix="scr_ex_p_gl_lib"):
        executor_id: int
        user_id: Optional[int]
        current_page_executor: int


class UpdateCallbackDataFilters:
    class SongTitleCollectionSongs(CallbackData, prefix="upd_s_t_coll_s"):
        pass

    class UserCollectionSongsPhotoFileId(CallbackData, prefix="upd_u_coll_s_p_f_id"):
        pass


class DeleteCallbackDataFilters:
    class SongCollectionSongs(CallbackData, prefix="del_s_coll_s"):
        pass

    class ButtonsDeleteSongColletionSongs(CallbackData, prefix="del_b_del_s_coll_s"):
        """Фильтр для размечивания песен как на готовые к удалению."""

        song_id: int
        position: int

    class ConfirmDeleteSongCollectionSongs(CallbackData, prefix="del_con_del_s_coll_s"):
        """Подтверждение на удаление песен."""

        pass

    class CompleteDeleteSongCollectionSongs(
        CallbackData, prefix="del_com_del_s_coll_s"
    ):
        """Cценарий удаления песен."""

        pass
