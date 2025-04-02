from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserData:
    browser: str
    os: str
    device: str

@dataclass(frozen=True)
class LocationData:
    city: str
    region: str
    country: str
    latitude: float | None
    longitude: float | None

@dataclass(frozen=True)
class JsData:
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
