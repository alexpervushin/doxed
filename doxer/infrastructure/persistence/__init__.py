from typing import TypeVar, Union

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

JsonValue = Union[str, int, float, bool, None, list['JsonValue'], dict[str, 'JsonValue']]
Document = dict[str, Union[BaseModel, JsonValue]]
Collection = AsyncIOMotorCollection[Document]

T = TypeVar('T')

from doxer.infrastructure.persistence.repositories import (
    UniqueLinkRepository,
    UsedTokenRepository,
    UserDataRepository,
)

__all__ = [
    "Document",
    "Collection",
    "UserDataRepository",
    "UniqueLinkRepository",
    "UsedTokenRepository",
]