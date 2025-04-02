
from doxer.domain.exceptions import (
    TokenInvalidError,
)
from doxer.domain.ports import (
    TokenHandlerProtocol,
    UsedTokenRepositoryProtocol,
)


class TokenValidator:

    def __init__(
        self,
        token_handler: TokenHandlerProtocol,
        used_token_repo: UsedTokenRepositoryProtocol,
    ) -> None:
        self._token_handler = token_handler
        self._used_token_repo = used_token_repo

    async def validate_token(self, token: str) -> None:
        if await self._used_token_repo.exists(token):
            raise TokenInvalidError("Token has already been used")

        if not await self._token_handler.verify_token(token):
            raise TokenInvalidError("Token is invalid, expired, or malformed")

