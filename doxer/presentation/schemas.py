from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserDataResponse(BaseModel):
    id: UUID
    ip_address: str
    browser_info: dict[str, str]
    location: dict[str, str | float | None]
    system_info: dict[str, str]
    timestamp: datetime
    link_name: Optional[str]


class CreateLinkResponse(BaseModel):
    name: str
    token: str


class CreateLinkPayload(BaseModel):
    name: str = Field(..., min_length=1, pattern=r'^[a-zA-Z0-9]+$')


class TrackPayload(BaseModel):
    token: str = Field(..., description="Tracking token associated with the link")
    name: Optional[str] = Field(None, description="Optional link name for identification")
    screen_resolution: str = Field(default="N/A")
    color_depth: str = Field(default="N/A")
    current_url: str = Field(default="N/A")
    time_zone: str = Field(default="N/A")
    language: str = Field(default="N/A")
    platform: str = Field(default="N/A")
    network_type: str = Field(default="N/A")
    battery_status: str = Field(default="N/A")
    device_memory: str = Field(default="N/A")
    logical_processors: str = Field(default="N/A")
    local_datetime: str = Field(default="N/A")
    webgl_renderer: str = Field(default="N/A")


class GetDataPayload(BaseModel):
    name: str = Field(..., description="Link name associated with the user data to retrieve")
