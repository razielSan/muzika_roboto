from typing import List
from domain.repositories.user import UserRepository


class GetOrCreateUser:
    def __init__(self, user_repo: UserRepository):
        self.user_repo: UserRepository = user_repo

    async def execute(
        self,
        name: str,
        telegram: int,
    ):

        # создаем жанры для пользователя
        user = await self.user_repo.get_user_by_telegram(telegram=telegram)
        if not user:
            user = await self.user_repo.create_user(name=name, telegram=telegram)
        return user
