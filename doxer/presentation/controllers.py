import io
import logging
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Header, Request, status
from fastapi.responses import StreamingResponse

from doxer.application.commands import (
    CreateUniqueLinkCommand,
    GenerateGifCommand,
)
from doxer.application.dtos import (
    CreateUniqueLinkInputDTO,
    CreateUniqueLinkOutputDTO,
    GenerateGifInputDTO,
    GenerateGifOutputDTO,
    UserDataOutputDTO,
    UserDataQueryDTO,
)
from doxer.application.queries import GetUserDataQuery
from doxer.presentation.schemas import (
    CreateLinkPayload,
    CreateLinkResponse,
    GetDataPayload,
    TrackPayload,
    UserDataResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/doxer", tags=["doxer"], route_class=DishkaRoute)


@router.post(
    "/links",
    response_model=CreateLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_link(
    command: FromDishka[CreateUniqueLinkCommand],
    payload: CreateLinkPayload,
    request: Request,
) -> CreateLinkResponse:
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Received request to create link from {client_host}. Payload: {payload.model_dump()}")
    try:
        input_dto = CreateUniqueLinkInputDTO(name=payload.name)
        app_dto: CreateUniqueLinkOutputDTO = await command.execute(input_dto)

        logger.info(f"Successfully created link '{app_dto.name}'. Token: {app_dto.token}")
        return app_dto
    except Exception as e:
        logger.error(f"Error during link creation for payload {payload.model_dump()}: {e}", exc_info=True)
        raise


@router.post(
    "/track",
    status_code=status.HTTP_200_OK,
)
async def track_and_get_gif(
    request: Request,
    command: FromDishka[GenerateGifCommand],
    payload: TrackPayload,
    user_agent: Annotated[str | None, Header()] = None,
) -> StreamingResponse:
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Received tracking request from {client_host}. Payload name: {payload.name}, Token: {payload.token[:5]}... User-Agent: {user_agent}")
    try:
        if user_agent is None:
            user_agent = "Unknown"

        input_dto = GenerateGifInputDTO(
            token=payload.token,
            name=payload.name,
            screen_resolution=payload.screen_resolution,
            color_depth=payload.color_depth,
            current_url=payload.current_url,
            time_zone=payload.time_zone,
            language=payload.language,
            platform=payload.platform,
            network_type=payload.network_type,
            battery_status=payload.battery_status,
            device_memory=payload.device_memory,
            logical_processors=payload.logical_processors,
            local_datetime=payload.local_datetime,
            webgl_renderer=payload.webgl_renderer,
            client_ip=client_host,
            user_agent=user_agent,
        )
        logger.debug(f"Prepared GenerateGifInputDTO: {input_dto}")

        result: GenerateGifOutputDTO = await command.execute(input_dto)

        logger.info(f"Successfully tracked data for token {payload.token[:5]}... UserData ID: {result.user_data_id}. Returning GIF.")
        return StreamingResponse(
            content=io.BytesIO(result.gif_bytes),
            media_type="image/gif",
            headers={"Cache-Control": "no-cache"},
        )
    except Exception as e:
        logger.error(f"Error during tracking for payload name {payload.name}, token {payload.token[:5]}...: {e}", exc_info=True)
        raise


@router.post(
    "/data",
    response_model=UserDataResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_data(
    query: FromDishka[GetUserDataQuery],
    payload: GetDataPayload,
    request: Request,
) -> UserDataResponse:
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Received request to get data from {client_host}. Payload: {payload.model_dump()}")
    try:
        query_dto = UserDataQueryDTO(name=payload.name)
        app_dto: UserDataOutputDTO = await query.execute(query_dto)
        response_model = UserDataResponse.model_validate(app_dto)
        logger.info(f"Successfully retrieved data for link name '{payload.name}'. UserData ID: {app_dto.id}")
        return response_model
    except Exception as e:
        logger.error(f"Error during data retrieval for payload {payload.model_dump()}: {e}", exc_info=True)
        raise
