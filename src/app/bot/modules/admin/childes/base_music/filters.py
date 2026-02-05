from aiogram.filters.callback_data import CallbackData


class BackExecutorCallback(CallbackData, prefix="back_executor"):
    executor_id: int


class BaseMusicCallback(CallbackData, prefix="base_music"):
    executor_id: int
    album_id: int
    
    
class PlaySongCallback(CallbackData, prefix="play_song"):
    position: int
    album_id: int