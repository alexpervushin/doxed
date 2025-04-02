import hashlib
import hmac
import time
from datetime import datetime
from uuid import uuid4

from doxer.domain.entities import UsedToken
from doxer.domain.ports import TokenHandlerProtocol, UsedTokenRepositoryProtocol
from doxer.infrastructure.config import HMAC as HMACSettings


class HMACTokenHandler(TokenHandlerProtocol):
    def __init__(
        self,
        settings: HMACSettings,
        used_token_repo: UsedTokenRepositoryProtocol,
    ) -> None:
        self._secret_key = settings.secret_key.encode()
        self._expire_minutes = settings.expire_minutes
        self._used_token_repo = used_token_repo

    async def verify_token(self, token: str) -> bool:
        try:
            timestamp_str, signature = token.split(".")
            token_timestamp = int(timestamp_str)

            current_timestamp = int(time.time())
            if token_timestamp < (current_timestamp - (self._expire_minutes * 60)):
                return False

            expected_signature = self._generate_signature(timestamp_str)
            if not hmac.compare_digest(signature, expected_signature):
                return False

            return True

        except (ValueError, AttributeError, TypeError):
            return False

    async def mark_as_used(self, token: str) -> None:
        await self._used_token_repo.create(
            UsedToken(
                id=uuid4(),
                token=token,
                used_at=datetime.now(),
            )
        )

    def _generate_signature(self, timestamp_str: str) -> str:
        return hmac.new(
            self._secret_key,
            timestamp_str.encode(),
            hashlib.sha256,
        ).hexdigest()

    def generate_token(self) -> str:
        timestamp = str(int(time.time()))
        signature = self._generate_signature(timestamp)
        return f"{timestamp}.{signature}"


class NoOpTokenHandler(TokenHandlerProtocol):
    async def verify_token(self, token: str) -> bool:
        return True

    async def mark_as_used(self, token: str) -> None:
        pass

    def generate_token(self) -> str:
        return f"hmac-disabled-{uuid4()}"
