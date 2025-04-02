import logging
from typing import Any, cast

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError

from doxer.domain.entities import UniqueLink, UsedToken, UserData
from doxer.domain.exceptions import (
    ConflictError,
    LinkNameExistsError,
    LinkNotFoundError,
    UserDataNotFoundError,
    ValidationError,
)
from doxer.domain.ports import (
    UniqueLinkRepositoryProtocol,
    UsedTokenRepositoryProtocol,
    UserDataRepositoryProtocol,
)
from doxer.domain.value_objects import BrowserData, JsData, LocationData

logger = logging.getLogger(__name__)

Collection = AsyncIOMotorCollection[dict[str, Any]]


class UserDataRepository(UserDataRepositoryProtocol):
    def __init__(self, collection: Collection) -> None:
        self._collection = collection
        logger.debug(
            f"UserDataRepository initialized with collection: {collection.name}"
        )

    async def create(self, user_data: UserData) -> UserData:
        document: dict[str, Any] = {
            "_id": user_data.id,
            "ip_address": user_data.ip_address,
            "browser_data": {
                "browser": user_data.browser_data.browser,
                "os": user_data.browser_data.os,
                "device": user_data.browser_data.device,
            },
            "location_data": {
                "city": user_data.location_data.city,
                "region": user_data.location_data.region,
                "country": user_data.location_data.country,
                "latitude": user_data.location_data.latitude,
                "longitude": user_data.location_data.longitude,
            },
            "js_data": {
                "screen_resolution": user_data.js_data.screen_resolution,
                "color_depth": user_data.js_data.color_depth,
                "current_url": user_data.js_data.current_url,
                "time_zone": user_data.js_data.time_zone,
                "language": user_data.js_data.language,
                "platform": user_data.js_data.platform,
                "network_type": user_data.js_data.network_type,
                "battery_status": user_data.js_data.battery_status,
                "device_memory": user_data.js_data.device_memory,
                "logical_processors": user_data.js_data.logical_processors,
                "local_datetime": user_data.js_data.local_datetime,
                "webgl_renderer": user_data.js_data.webgl_renderer,
            },
            "timestamp": user_data.timestamp,
            "token": user_data.token,
            "link_name": user_data.link_name,
        }
        document = {k: v for k, v in document.items() if v is not None}
        logger.debug(
            f"Attempting to insert UserData document into {self._collection.name}: {document}"
        )
        try:
            result = await self._collection.insert_one(document)
            logger.info(
                f"Successfully inserted UserData document with _id: {result.inserted_id} into {self._collection.name}"
            )
            return user_data
        except DuplicateKeyError as e:
            logger.error(
                f"Duplicate key error while inserting UserData into {self._collection.name}. Document: {document}",
                exc_info=True,
            )
            raise ConflictError(f"UserData conflict: {e}") from e
        except Exception as e:
            logger.error(
                f"Error inserting UserData document into {self._collection.name}: {document}",
                exc_info=True,
            )
            raise

    async def get_by_token(self, token: str) -> UserData:
        logger.debug(
            f"Attempting to find UserData by token {token[:5]}... in {self._collection.name}"
        )
        document = await self._collection.find_one({"token": token})
        if not document:
            logger.warning(
                f"UserData not found for token {token[:5]}... in {self._collection.name}"
            )
            raise UserDataNotFoundError(token)
        logger.debug(
            f"Found UserData document for token {token[:5]}... in {self._collection.name}"
        )

        doc = cast(dict[str, Any], document)
        return UserData(
            id=doc["_id"],
            ip_address=doc["ip_address"],
            browser_data=BrowserData(**doc["browser_data"]),
            location_data=LocationData(**doc["location_data"]),
            js_data=JsData(
                screen_resolution=doc["js_data"]["screen_resolution"],
                color_depth=doc["js_data"]["color_depth"],
                current_url=doc["js_data"]["current_url"],
                time_zone=doc["js_data"]["time_zone"],
                language=doc["js_data"]["language"],
                platform=doc["js_data"]["platform"],
                network_type=doc["js_data"]["network_type"],
                battery_status=doc["js_data"]["battery_status"],
                device_memory=doc["js_data"]["device_memory"],
                logical_processors=doc["js_data"]["logical_processors"],
                local_datetime=doc["js_data"]["local_datetime"],
                webgl_renderer=doc["js_data"]["webgl_renderer"],
            ),
            timestamp=doc["timestamp"],
            token=doc["token"],
            link_name=doc.get("link_name"),
        )


class UniqueLinkRepository(UniqueLinkRepositoryProtocol):
    def __init__(self, collection: Collection) -> None:
        self._collection = collection
        logger.debug(
            f"UniqueLinkRepository initialized with collection: {collection.name}"
        )

    async def create(self, link: UniqueLink) -> UniqueLink:
        document: dict[str, Any] = {
            "_id": link.id,
            "name": link.name,
            "token": link.token,
            "created_at": link.created_at,
        }
        logger.debug(
            f"Attempting to insert UniqueLink document into {self._collection.name}: {document}"
        )
        try:
            result = await self._collection.insert_one(document)
            logger.info(
                f"Successfully inserted UniqueLink document with _id: {result.inserted_id} into {self._collection.name}"
            )
        except DuplicateKeyError as e:
            key_pattern = e.details.get("keyPattern", {}) if e.details else {}
            key_value = e.details.get("keyValue", {}) if e.details else {}
            logger.error(
                f"Duplicate key error while inserting UniqueLink into {self._collection.name}. "
                f"Document attempted: {document}. Error details: {e.details}. "
                f"Key Pattern: {key_pattern}, Key Value: {key_value}",
                exc_info=True,
            )
            if "name" in key_pattern and key_value.get("name") == link.name:
                logger.warning(f"Duplicate name detected for UniqueLink: '{link.name}'")
                raise LinkNameExistsError(link.name) from e
            logger.error(
                f"Unhandled DuplicateKeyError for UniqueLink: {document}", exc_info=True
            )
            raise ConflictError(f"UniqueLink conflict: {e}") from e
        except Exception as e:
            logger.error(
                f"Error inserting UniqueLink document into {self._collection.name}: {document}",
                exc_info=True,
            )
            raise
        return link

    async def get_by_name(self, name: str) -> UniqueLink:
        logger.debug(
            f"Attempting to find UniqueLink by name '{name}' in {self._collection.name}"
        )
        document = await self._collection.find_one({"name": name})
        if not document:
            logger.warning(
                f"UniqueLink not found for name '{name}' in {self._collection.name}"
            )
            raise LinkNotFoundError(name)
        logger.debug(
            f"Found UniqueLink document for name '{name}' in {self._collection.name}"
        )

        doc = cast(dict[str, Any], document)
        return UniqueLink(
            id=doc["_id"],
            name=doc["name"],
            token=doc["token"],
            created_at=doc["created_at"],
        )

    async def exists(self, name: str) -> bool:
        logger.debug(
            f"Checking existence of UniqueLink with name '{name}' in {self._collection.name}"
        )
        count = await self._collection.count_documents({"name": name}, limit=1)
        exists = count > 0
        logger.debug(
            f"UniqueLink with name '{name}' exists: {exists} in {self._collection.name}"
        )
        return exists


class UsedTokenRepository(UsedTokenRepositoryProtocol):
    def __init__(self, collection: Collection) -> None:
        self._collection = collection
        logger.debug(
            f"UsedTokenRepository initialized with collection: {collection.name}"
        )

    async def create(self, used_token: UsedToken) -> UsedToken:
        if not used_token.token:
            logger.error(
                "Attempted to create UsedToken with null or empty token value."
            )
            raise ValidationError("Used token value cannot be null or empty.")

        document: dict[str, Any] = {
            "_id": used_token.id,
            "token": used_token.token,
            "used_at": used_token.used_at,
        }
        logger.debug(
            f"Attempting to insert UsedToken document into {self._collection.name}: {{'_id': {document['_id']}, 'token': '{document['token'][:5]}...'}}"
        )
        result = await self._collection.insert_one(document)
        logger.info(
            f"Successfully inserted UsedToken document with _id: {result.inserted_id} into {self._collection.name}"
        )
        return used_token

    async def exists(self, token: str) -> bool:
        if not token:
            logger.warning(
                "Checked existence for null or empty token in UsedTokenRepository."
            )
            return False
        logger.debug(
            f"Checking existence of UsedToken with token {token[:5]}... in {self._collection.name}"
        )
        count = await self._collection.count_documents({"token": token}, limit=1)
        exists = count > 0
        logger.debug(f"UsedToken with token {token[:5]}... exists: {exists} in {self._collection.name}")
        return count > 0