from typing import Optional

from pydantic import BaseModel, Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict

from doxer.infrastructure.persistence.constants import (
    LINKS_COLLECTION,
    USED_TOKENS_COLLECTION,
    USER_DATA_COLLECTION,
)


class MongoDB(BaseModel):
    uri: str
    db_name: str
    user_data_collection: str = USER_DATA_COLLECTION
    used_tokens_collection: str = USED_TOKENS_COLLECTION
    links_collection: str = LINKS_COLLECTION

class Telegram(BaseModel):
    bot_token: str
    channel_id: str

class HMAC(BaseModel):
    secret_key: str = Field(min_length=32)
    expire_minutes: PositiveInt = 60

class Server(BaseModel):
    port: int = 8000
    workers: int = 1
    root_path: str = ""

class Runner(BaseModel):
    workers: int = 1


class Settings(BaseSettings):
    mongodb: MongoDB
    telegram: Telegram
    hmac: Optional[HMAC] = None
    server: Server
    runner: Runner
    templates_dir: str = "templates"
    static_dir: str = "static"
    gif_template_path: str = "happy.gif"
    font_path: Optional[str] = None

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

def get_settings() -> Settings:
    return Settings() # noqa
