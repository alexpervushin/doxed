from dishka import Provider, Scope, provide
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)
from pydantic_settings import BaseSettings

from doxer.application.commands import CreateUniqueLinkCommand, GenerateGifCommand
from doxer.application.queries import GetUserDataQuery
from doxer.domain.ports import (
    GifGeneratorProtocol,
    IdGeneratorProtocol,
    LocationServiceProtocol,
    NotificationServiceProtocol,
    TokenHandlerProtocol,
    UniqueLinkRepositoryProtocol,
    UsedTokenRepositoryProtocol,
    UserDataRepositoryProtocol,
)
from doxer.domain.validators import TokenValidator
from doxer.infrastructure.config import Settings, get_settings
from doxer.infrastructure.external.location_service import IpApiLocationService
from doxer.infrastructure.external.telegram_notifier import TelegramNotifier
from doxer.infrastructure.media.gif_generator import ImageIOGifGenerator
from doxer.infrastructure.persistence.repositories import (
    UniqueLinkRepository,
    UsedTokenRepository,
    UserDataRepository,
)
from doxer.infrastructure.security.token_handler import (
    HMACTokenHandler,
    NoOpTokenHandler,
)
from doxer.infrastructure.utils import UuidGenerator


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_settings(self) -> Settings:
        return get_settings()

    @provide(scope=Scope.APP)
    async def provide_base_settings(self, settings: Settings) -> BaseSettings:
        return settings


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_client(self, settings: Settings) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(settings.mongodb.uri, uuidRepresentation="standard")

    @provide(scope=Scope.REQUEST)
    def get_database(
        self, client: AsyncIOMotorClient, settings: Settings
    ) -> AsyncIOMotorDatabase:
        return client[settings.mongodb.db_name]


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_data_repository(
        self, database: AsyncIOMotorDatabase, settings: Settings
    ) -> UserDataRepositoryProtocol:
        collection = database[settings.mongodb.user_data_collection]
        return UserDataRepository(collection)

    @provide(scope=Scope.REQUEST)
    def get_used_token_repository(
        self, database: AsyncIOMotorDatabase, settings: Settings
    ) -> UsedTokenRepositoryProtocol:
        collection = database[settings.mongodb.used_tokens_collection]
        return UsedTokenRepository(collection)

    @provide(scope=Scope.REQUEST)
    def get_unique_link_repository(
        self, database: AsyncIOMotorDatabase, settings: Settings
    ) -> UniqueLinkRepositoryProtocol:
        collection = database[settings.mongodb.links_collection]
        return UniqueLinkRepository(collection)


class ExternalServicesProvider(Provider):
    @provide(scope=Scope.APP)
    def get_location_service(self) -> LocationServiceProtocol:
        return IpApiLocationService()

    @provide(scope=Scope.APP)
    def get_notification_service(
        self, settings: Settings
    ) -> NotificationServiceProtocol:
        return TelegramNotifier(settings.telegram)


class MediaProvider(Provider):
    @provide(scope=Scope.APP)
    def get_gif_generator(self, settings: Settings) -> GifGeneratorProtocol:
        return ImageIOGifGenerator(
            template_path=settings.gif_template_path,
            font_path=settings.font_path,
        )


class SecurityProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_token_handler(
        self,
        settings: Settings,
        used_token_repo: UsedTokenRepositoryProtocol,
    ) -> TokenHandlerProtocol:
        if settings.hmac:
            return HMACTokenHandler(settings.hmac, used_token_repo)
        else:
            return NoOpTokenHandler()

    @provide(scope=Scope.APP)
    def get_id_generator(self) -> IdGeneratorProtocol:
        return UuidGenerator()

    @provide(scope=Scope.REQUEST)
    def get_token_validator(
        self,
        token_handler: TokenHandlerProtocol,
        used_token_repo: UsedTokenRepositoryProtocol,
    ) -> TokenValidator:
        return TokenValidator(token_handler, used_token_repo)


class DoxerProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_create_unique_link_command(
        self,
        id_generator: IdGeneratorProtocol,
        link_repo: UniqueLinkRepositoryProtocol,
        token_handler: TokenHandlerProtocol,
    ) -> CreateUniqueLinkCommand:
        return CreateUniqueLinkCommand(
            id_generator=id_generator,
            link_repo=link_repo,
            token_handler=token_handler,
        )

    @provide(scope=Scope.REQUEST)
    def get_generate_gif_command(
        self,
        id_generator: IdGeneratorProtocol,
        user_data_repo: UserDataRepositoryProtocol,
        token_validator: TokenValidator,
        token_handler: TokenHandlerProtocol,
        location_service: LocationServiceProtocol,
        gif_generator: GifGeneratorProtocol,
        notifier: NotificationServiceProtocol,
    ) -> GenerateGifCommand:
        return GenerateGifCommand(
            id_generator=id_generator,
            user_data_repo=user_data_repo,
            token_validator=token_validator,
            token_handler=token_handler,
            location_service=location_service,
            gif_generator=gif_generator,
            notifier=notifier,
        )

    @provide(scope=Scope.REQUEST)
    def get_user_data_query(
        self,
        user_data_repo: UserDataRepositoryProtocol,
        link_repo: UniqueLinkRepositoryProtocol,
    ) -> GetUserDataQuery:
        return GetUserDataQuery(user_data_repo=user_data_repo, link_repo=link_repo)