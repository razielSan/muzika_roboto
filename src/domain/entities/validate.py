from domain.errors.error_code import ErorrCode, SuccessCode
from core.error_handlers.helpers import ok, fail


class UserValidator:
    def __init__(
        self,
        name=None,
        telegram=None,
    ):
        self.name = name
        self.telegram = telegram

    def validate_name(self):
        if not isinstance(self.name, str):
            return fail(
                code=ErorrCode.INVALID_USER_NAME.name,
                message=ErorrCode.INVALID_USER_NAME.value,
            )

        if len(self.name.strip()) == 0:
            return fail(
                code=ErorrCode.INVALID_LEN_DATA.name,
                message=ErorrCode.INVALID_LEN_DATA.value,
            )

        return ok(
            data=self.name.strip(),
            code=SuccessCode.VALIDATE_USER_SUCCES.name,
        )

    def validate_telegram(self):
        if not isinstance(self.telegram, int):
            return fail(
                code=ErorrCode.INVALID_TELEGRAM.name,
                message=ErorrCode.INVALID_TELEGRAM.value,
            )

        return ok(
            data=self.telegram,
            code=SuccessCode.VALIDATE_USER_SUCCES.name,
        )


class ExecutorValidator:
    def __init__(self, name=None, country=None, genres=None, user_id=None):
        self.name = name
        self.country = country
        self.genres = genres
        self.user_id = user_id

    def validate_name(self):
        if not isinstance(self.name, str):
            return fail(
                code=ErorrCode.INVALID_EXECUTOR_NAME.name,
                message=ErorrCode.INVALID_EXECUTOR_NAME.value,
            )
        if len(self.name.strip()) == 0:
            return fail(
                code=ErorrCode.INVALID_LEN_DATA.name,
                message=ErorrCode.INVALID_LEN_DATA.value,
            )

        return ok(
            data=self.name.strip(),
            code=SuccessCode.VALIDATE_EXECUTOR_SUCCESS.name,
        )

    def validate_country(self):
        if not isinstance(self.country, str):
            return fail(
                code=ErorrCode.INVALID_EXECUTOR_COUNTRY.name,
                message=ErorrCode.INVALID_EXECUTOR_COUNTRY.value,
            )

        if len(self.country.strip()) == 0:
            return fail(
                code=ErorrCode.INVALID_LEN_DATA.name,
                message=ErorrCode.INVALID_LEN_DATA.value,
            )

        return ok(
            data=self.country.strip(),
            code=SuccessCode.VALIDATE_EXECUTOR_SUCCESS.name,
        )

    def validate_genres(self):
        if not isinstance(self.genres, list):
            return fail(
                code=ErorrCode.INVALID_EXECUTOR_GENRES.name,
                message=ErorrCode.INVALID_EXECUTOR_GENRES.value,
            )
        if len(self.genres) == 0:
            return fail(
                code=ErorrCode.INVALID_LEN_DATA.name,
                message=ErorrCode.INVALID_LEN_DATA.value,
            )

        return ok(
            data=self.genres,
            code=SuccessCode.VALIDATE_EXECUTOR_SUCCESS.name,
        )

    def validate_user_id(self):
        if not isinstance(self.user_id, (int, type(None))):
            return fail(
                code=ErorrCode.INVALID_USER_ID.name,
                message=ErorrCode.INVALID_USER_ID.value,
            )
        return ok(
            data=self.user_id,
            code=SuccessCode.VALIDATE_EXECUTOR_SUCCESS.name,
        )


class AlbumValidator:
    def __init__(self, album_id=None, executor_id=None, user_id=None):
        self.album_id = album_id
        self.executor_id = executor_id
        self.user_id = user_id

    def validate_executor_id(self):
        if not isinstance(self.executor_id, int):
            return fail(
                code=ErorrCode.INVALID_EXECUTOR_ID.name,
                message=ErorrCode.INVALID_EXECUTOR_ID.value,
            )

        return ok(
            data=self.executor_id,
            code=SuccessCode.VALIDATE_ALBUM_SUCCESS.name,
        )

    def validate_album_id(self):
        if not isinstance(self.album_id, int):
            return fail(
                code=ErorrCode.INVALID_ALBUM_ID.name,
                message=ErorrCode.INVALID_ALBUM_ID.value,
            )

        return ok(
            data=self.album_id,
            code=SuccessCode.VALIDATE_ALBUM_SUCCESS.name,
        )

    def validate_user_id(self):
        if not isinstance(self.user_id, (int, type(None))):
            return fail(
                code=ErorrCode.INVALID_USER_ID.name,
                message=ErorrCode.INVALID_USER_ID.value,
            )
        return ok(
            data=self.user_id,
            code=SuccessCode.VALIDATE_ALBUM_SUCCESS.name,
        )
