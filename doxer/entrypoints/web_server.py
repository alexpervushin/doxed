import logging
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from doxer.infrastructure.config import Settings, get_settings
from doxer.infrastructure.di import container
from doxer.infrastructure.http.exceptions_handler import register_exception_handlers
from doxer.infrastructure.persistence.constants import NAME_INDEX, TOKEN_INDEX
from doxer.presentation.controllers import router as doxer_router

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan...")
    app_settings: Settings = await container.get(Settings)
    client: AsyncIOMotorClient = await container.get(AsyncIOMotorClient)
    db = client[app_settings.mongodb.db_name]
    logger.info(
        f"Connected to MongoDB: {app_settings.mongodb.uri}, DB: {app_settings.mongodb.db_name}"
    )

    try:
        user_data_coll = db[app_settings.mongodb.user_data_collection]
        await user_data_coll.create_index("token", name=TOKEN_INDEX)
        logger.debug(
            f"Ensured index '{TOKEN_INDEX}' on collection '{app_settings.mongodb.user_data_collection}'"
        )

        used_tokens_coll = db[app_settings.mongodb.used_tokens_collection]
        await used_tokens_coll.create_index("token", name=TOKEN_INDEX, unique=True)
        logger.debug(
            f"Ensured unique index '{TOKEN_INDEX}' on collection '{app_settings.mongodb.used_tokens_collection}'"
        )

        links_coll = db[app_settings.mongodb.links_collection]
        logger.debug(
            f"Attempting to ensure unique index '{NAME_INDEX}' on collection '{app_settings.mongodb.links_collection}'"
        )
        await links_coll.create_index("name", name=NAME_INDEX, unique=True)
        logger.info(
            f"Successfully ensured unique index '{NAME_INDEX}' on collection '{app_settings.mongodb.links_collection}'"
        )

    except Exception as e:
        logger.error(
            f"Error during index creation: {e}", exc_info=True
        )
        raise

    logger.info("Application startup complete. Yielding control.")
    yield
    logger.info("Starting application shutdown...")
    await container.close()
    logger.info("DI container closed.")
    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    logger.info("Creating FastAPI application...")
    app = FastAPI(lifespan=lifespan)

    setup_dishka(container, app)
    register_exception_handlers(
        app
    )

    routers = (doxer_router,)
    for router in routers:
        app.include_router(router)
        logger.debug(f"Included router with prefix: {router.prefix}")

    logger.info("FastAPI application created successfully.")
    return app


if __name__ == "__main__":
    settings = get_settings()
    logger.info(
        f"Starting Uvicorn server on 0.0.0.0:{settings.server.port} with {settings.server.workers} workers..."
    )
    uvicorn.run(
        "doxer.entrypoints.web_server:create_app",
        factory=True,
        workers=settings.server.workers,
        host="0.0.0.0",
        port=settings.server.port,
        root_path=settings.server.root_path or "",
        log_config=None,
    )