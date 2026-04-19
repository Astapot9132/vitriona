from dependency_injector import containers, providers
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cfg import Cfg
from src.app.core.config import get_settings
from src.app.core.security import SecurityService
from src.modules.shared.unit_of_work import UnitOfWork


async def api_uow():
    uow = container.api_uow()
    async with uow:
        yield uow


class Container(containers.DeclarativeContainer):
    cfg = providers.Singleton(Cfg)

    settings = providers.Singleton(get_settings)
    api_engine = providers.Singleton(
        create_async_engine,
        isolation_level="READ COMMITTED",
        url=cfg.provided.database_url,
        pool_pre_ping=True,
    )
    api_sessionmaker = providers.Singleton(
        async_sessionmaker,
        bind=api_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    api_uow = providers.Factory(UnitOfWork, session_factory=api_sessionmaker)
    security_service = providers.Singleton(SecurityService, settings=settings)


container = Container()


def require_auth(request: Request):
    return container.security_service().require_auth(request)
