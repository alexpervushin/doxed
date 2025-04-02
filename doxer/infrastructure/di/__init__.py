from dishka import make_async_container

from doxer.infrastructure.di.providers import (
    ConfigProvider,
    DatabaseProvider,
    DoxerProvider,
    ExternalServicesProvider,
    MediaProvider,
    RepositoryProvider,
    SecurityProvider,
)

container = make_async_container(
    ConfigProvider(),
    DatabaseProvider(),
    RepositoryProvider(),
    ExternalServicesProvider(),
    MediaProvider(),
    SecurityProvider(),
    DoxerProvider(),
)

