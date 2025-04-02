import asyncio
import io
from pathlib import Path
from typing import cast

import imageio
import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageDraw, ImageFont

from doxer.domain.entities import UserData
from doxer.domain.ports import GifGeneratorProtocol


class ImageIOGifGenerator(GifGeneratorProtocol):
    def __init__(
        self,
        template_path: str,
        font_path: str | None = None,
        font_size: int = 13,
    ) -> None:
        self._template_path = Path(template_path)
        self._font_size = font_size
        if font_path:
            try:
                self._font = ImageFont.truetype(font_path, size=font_size)
            except IOError:
                default_font = ImageFont.load_default()
                self._font = ImageFont.truetype(default_font.path, size=font_size)
        else:
            default_font = ImageFont.load_default()
            self._font = ImageFont.truetype(default_font.path, size=font_size)

    async def create_gif_with_text(self, user_data: UserData) -> bytes:
        text_lines = self._prepare_text_lines(user_data)
        text = "\n".join(text_lines)

        reader = imageio.get_reader(str(self._template_path))
        frames = await asyncio.gather(
            *[
                self._process_frame(cast(NDArray[np.uint8], frame), text)
                for frame in reader
            ]
        )

        gif_bytes_io = io.BytesIO()

        await asyncio.to_thread(
            imageio.mimsave,
            gif_bytes_io,
            frames,
            format="GIF",
            duration=reader.get_meta_data()["duration"] / 1000.0,
            loop=0,
        )

        gif_bytes = gif_bytes_io.getvalue()
        gif_bytes_io.close()

        return gif_bytes

    async def _process_frame(
        self, frame: NDArray[np.uint8], text: str
    ) -> NDArray[np.uint8]:
        img = await asyncio.to_thread(Image.fromarray, frame)
        img = await asyncio.to_thread(img.convert, "RGBA")

        draw = ImageDraw.Draw(img)

        bbox = await asyncio.to_thread(
            draw.multiline_textbbox, (0, 0), text, font=self._font
        )
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((img.width - text_width) // 2, (img.height - text_height) // 2)

        await asyncio.to_thread(
            draw.multiline_text,
            position,
            text,
            font=self._font,
            fill=(255, 255, 255, 255),
            align="center",
        )

        return await asyncio.to_thread(np.array, img)

    def _prepare_text_lines(self, user_data: UserData) -> list[str]:
        lines: list[str] = []

        if user_data.link_name:
            lines.append(f"Link: {user_data.link_name}")
        lines.append(f"IP: {user_data.ip_address}")

        lines.append(f"Browser: {user_data.browser_data.browser}")
        lines.append(f"OS: {user_data.browser_data.os}")
        if user_data.browser_data.device != "Other":
            lines.append(f"Device: {user_data.browser_data.device}")

        location_parts: list[str] = []
        if user_data.location_data.city != "N/A":
            location_parts.append(user_data.location_data.city)
        if user_data.location_data.region != "N/A":
            location_parts.append(user_data.location_data.region)
        if user_data.location_data.country != "N/A":
            location_parts.append(user_data.location_data.country)
        if location_parts:
            lines.append(f"Location: {', '.join(location_parts)}")

        if (
            user_data.location_data.latitude is not None
            and user_data.location_data.longitude is not None
        ):
            lines.append(
                f"Coordinates: {user_data.location_data.latitude}, {user_data.location_data.longitude}"
            )

        js_data = user_data.js_data
        lines.extend(
            [
                f"Screen: {js_data.screen_resolution}",
                f"Color Depth: {js_data.color_depth}",
                f"Time Zone: {js_data.time_zone}",
                f"Language: {js_data.language}",
                f"Platform: {js_data.platform}",
                f"Network: {js_data.network_type}",
                f"Battery: {js_data.battery_status}",
                f"Memory: {js_data.device_memory}",
                f"Processors: {js_data.logical_processors}",
                f"Local Time: {js_data.local_datetime}",
                f"WebGL: {js_data.webgl_renderer}",
            ]
        )

        return lines
