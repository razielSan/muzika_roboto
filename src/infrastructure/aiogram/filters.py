from typing import Optional, Union, Any

from aiogram.filters.callback_data import CallbackData


class BackMenuUserPanel(CallbackData, prefix="back_menu_u_p"):
    pass


class BackAdminMenuCallback(CallbackData, prefix="back_admin_menu"):
    pass


class BackExecutorPage(CallbackData, prefix="back_exc_p"):
    user_id: Optional[int]
    album_position: int
    current_page: int
    is_admin: bool


class BackAlbumPage(CallbackData, prefix="back_a_p"):
    user_id: Optional[int]
    album_id: int
    album_position: int
    current_page_executor: int
    is_global_executor: bool
    executor_id: int
    is_admin: bool


class PlaySongsAlbums(CallbackData, prefix="play_s_coll_s"):
    song_id: int
    album_id: int


class PlaySongsCollectionSongs(CallbackData, prefix="play_s_coll_s"):
    song_id: int


class StartUserLibrary(CallbackData, prefix="start_u_l"):
    pass


class StartGlobalLibrary(CallbackData, prefix="start_g_l"):
    is_admin: bool


class Search(CallbackData, prefix="search"):
    class Executor(CallbackData, prefix="search_ex"):
        is_admin: bool

    class ExecutorName(CallbackData, prefix="search_ex_n"):
        """Сценария для поиска исполнителя по имени."""

        is_admin: bool

    class ExecutorGenres(CallbackData, prefix="search_ex_g"):
        """Сценария для поиска исполнителя по жанрам."""

        is_admin: bool

    class ExecutorGenreButton(CallbackData, prefix="search_exc_g_b"):
        order: int
        is_admin: bool

    class ExecutorButton(CallbackData, prefix="search_ex_b"):
        """
        Сценария для отображение на кнопке клавиатуры исполнителя,который найден.
        """

        id: int
        is_admin: bool


class ShowAlbumExecutor(CallbackData, prefix="show_al_ex"):
    album_position: int
    album_id: int
    user_id: Optional[int]
    executor_id: int
    current_page_executor: int
    is_global_executor: bool
    is_admin: Union[bool, int]


class SyncExecutor(CallbackData, prefix="sync_ex"):
    executor_id: int


class DesyncExecutor(CallbackData, prefix="desync_ex"):
    executor_id: int


class AddCallbackDataFilters:
    class SongCollectionSongs(CallbackData, prefix="add_coll_s"):
        pass

    class AddAlbumExecutor(CallbackData, prefix="add_a_exc"):
        executor_id: int
        user_id: Optional[int]
        current_page_executor: int
        is_admin: bool

    class AddSongsAlbum(CallbackData, prefix="add_s_a"):
        executor_id: int
        album_id: int
        user_id: Optional[int]
        current_page_executor: int
        album_position: int
        is_global_executor: bool
        is_admin: bool


class ScrollingCallbackDataFilters:
    class SongCollectionSongs(CallbackData, prefix="scr_s_coll_s"):
        position: int
        offset: int

    class DeleteMenuSongColletionSongs(CallbackData, prefix="scr_del_menu_coll_s"):
        """Фильтр для пролистывания песен в меню удаления песен сборника."""

        position: int
        offset: int

    class DeleteMenuSongAlbum(CallbackData, prefix="scr_del_menu_a"):
        """Фильтр для пролистывания песен в меню удаления песен альбома."""

        position: int
        offset: int

    class SongsAlbumLibrary(CallbackData, prefix="scr_s_al_gl_lib"):
        album_position: int
        user_id: Optional[int]
        position: int
        offset: int
        executor_id: int
        current_page_executor: int
        is_global_executor: bool
        album_id: int
        is_admin: bool

    class AlbumsExecutorLibrary(CallbackData, prefix="scr_al_ex_gl_lib"):
        executor_id: int
        user_id: Optional[int]
        current_page_executor: int
        position: int
        offset: int
        is_admin: bool

    class ExecutorPageLibrary(CallbackData, prefix="scr_ex_p_gl_lib"):
        executor_id: int
        user_id: Optional[int]
        current_page_executor: int
        is_admin: bool

    class SearchExecutor(CallbackData, prefix="scr_search_ex"):
        position: int
        offset: int
        is_admin: bool


class UpdateCallbackDataFilters:
    class SongTitleCollectionSongs(CallbackData, prefix="upd_s_t_coll_s"):
        pass

    class UserCollectionSongsPhotoFileId(CallbackData, prefix="upd_u_coll_s_p_f_id"):
        pass

    class UserExecutorPhotoFileId(CallbackData, prefix="upd_u_exc_p_f_id"):
        excecutor_id: int
        user_id: Optional[int]
        current_page_executor: int
        album_position: int
        is_admin: bool

    class UserExecutorCountry(CallbackData, prefix="upd_u_exc_c"):
        excecutor_id: int
        user_id: Optional[int]
        current_page_executor: int
        album_position: int
        is_admin: bool

    class UserExecutorGenres(CallbackData, prefix="upd_u_exc_g"):
        excecutor_id: int
        user_id: Optional[int]
        current_page_executor: int
        album_position: int
        is_admin: bool

    class UserExecutorName(CallbackData, prefix="upd_u_exc_n"):
        country: str
        excecutor_id: int
        user_id: Optional[int]
        current_page_executor: int
        album_position: int
        is_admin: bool

    class AlbumPhoto(CallbackData, prefix="upd_a_p"):
        executor_id: int
        album_id: int
        user_id: Optional[int]
        current_page_executor: int
        is_global_executor: bool
        is_admin: bool
        album_position: int

    class AlbumYear(CallbackData, prefix="upd_a_y"):
        executor_id: int
        album_id: int
        user_id: Optional[int]
        current_page_executor: int
        is_admin: bool
        is_global_executor: bool
        album_position: int

    class AlbumTitle(CallbackData, prefix="upd_a_t"):
        executor_id: int
        album_id: int
        user_id: Optional[int]
        current_page_executor: int
        is_global_executor: bool
        is_admin: bool
        album_position: int

    class SongTitle(CallbackData, prefix="upd_s_t"):
        executor_id: int
        album_id: int
        user_id: Optional[int]
        current_page_executor: int
        is_global_executor: bool
        is_admin: bool
        album_position: int


class DeleteCallbackDataFilters:

    # удаление песен из сборника
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

    class SongCollectionSongs(CallbackData, prefix="del_s_coll_s"):
        pass

    # удаление песен из альбома
    class SongsAlbum(CallbackData, prefix="del_s_a"):
        executor_id: int
        album_id: int
        user_id: Optional[int]
        current_page_executor: int
        is_global_executor: bool
        album_position: int
        is_admin: bool

    class ButtonsDeleteSongAlbum(CallbackData, prefix="del_b_s_a"):
        """Фильтр для размечивания песен как на готовые к удалению в альбоме."""

        song_id: int
        position: int

    class ConfirmDeleteSongAlbum(CallbackData, prefix="del_con_s_a"):
        """Подтверждение на удаление песен в альбоме."""

        is_admin: bool

    class CompleteDeleteSongAlbum(CallbackData, prefix="del_com_s_a"):
        """Завершение удаление песен из альбома."""

        is_admin: bool

    # удаление исполнителя
    class ConfirmDeleteExecutor(CallbackData, prefix="del_con_exc"):
        user_id: Optional[int]
        executor_id: int
        current_page_executor: int
        album_position: int
        is_admin: bool

    class CompleteDeleteExecutor(CallbackData, prefix="del_com_exc"):
        user_id: Optional[int]
        executor_id: int
        current_page_executor: int
        is_admin: bool

    # удаление альбома
    class ConfirmDeleteAlbum(CallbackData, prefix="del_con_del_a"):
        executor_id: int
        album_id: int
        user_id: Optional[int]
        current_page_executor: int
        is_global_executor: bool
        album_position: int
        is_admin: bool

    class CompleteDeleteAlbum(CallbackData, prefix="del_com_del_a"):
        user_id: Optional[int]
        executor_id: int
        current_page_executor: int
        album_id: int
        is_admin: bool
