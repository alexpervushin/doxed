from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from doxer.domain.value_objects import BrowserData, JsData, LocationData


@dataclass
class BaseEntity:
    id: UUID

@dataclass
class UserData(BaseEntity):
    ip_address: str
    browser_data: BrowserData
    location_data: LocationData
    js_data: JsData
    timestamp: datetime
    token: str
    link_name: Optional[str] = field(default=None)

@dataclass
class UniqueLink(BaseEntity):
    name: str
    token: str
    created_at: datetime

@dataclass
class UsedToken(BaseEntity):
    token: str
    used_at: datetime
