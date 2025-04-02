from typing import Any

import aiohttp
from pydantic import ValidationError

from doxer.domain.exceptions import ValidationError as DomainValidationError
from doxer.domain.ports import LocationServiceProtocol
from doxer.domain.value_objects import LocationData


class IpApiLocationService(LocationServiceProtocol):
    def __init__(self, base_url: str = "https://ipapi.co") -> None:
        self._base_url = base_url.rstrip("/")

    async def get_location_data(self, ip_address: str) -> LocationData:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._base_url}/{ip_address}/json/") as response:
                if response.status != 200:
                    return self._create_default_location()

                try:
                    data: dict[str, Any] = await response.json()
                    return self._parse_location_data(data)
                except (aiohttp.ClientError, ValidationError) as e:
                    raise DomainValidationError(
                        f"Failed to fetch location data: {str(e)}"
                    )

    def _parse_location_data(self, data: dict[str, Any]) -> LocationData:
        return LocationData(
            city=str(data.get("city", "N/A")),
            region=str(data.get("region", "N/A")),
            country=str(data.get("country_name", "N/A")),
            latitude=float(data["latitude"]) if "latitude" in data else None,
            longitude=float(data["longitude"]) if "longitude" in data else None,
        )

    def _create_default_location(self) -> LocationData:
        return LocationData(
            city="N/A",
            region="N/A",
            country="N/A",
            latitude=None,
            longitude=None,
        )