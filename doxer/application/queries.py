from dishka import FromDishka

from doxer.application.dtos import UserDataOutputDTO, UserDataQueryDTO
from doxer.domain.entities import UniqueLink, UserData
from doxer.domain.ports import (
    UniqueLinkRepositoryProtocol,
    UserDataRepositoryProtocol,
)


class GetUserDataQuery:
    def __init__(
        self,
        user_data_repo: FromDishka[UserDataRepositoryProtocol],
            link_repo: FromDishka[UniqueLinkRepositoryProtocol],
    ) -> None:
        self._user_data_repo = user_data_repo
        self._link_repo = link_repo

    async def execute(self, dto: UserDataQueryDTO) -> UserDataOutputDTO:
        link: UniqueLink = await self._link_repo.get_by_name(dto.name)

        user_data: UserData = await self._user_data_repo.get_by_token(link.token)

        return UserDataOutputDTO.from_entity(user_data)

