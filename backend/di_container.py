from dependency_injector import containers, providers
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cfg import Cfg, ADB_URL
from src.app.core.config import get_settings
from src.app.core.security import SecurityService
from src.modules.shared.unit_of_work import UnitOfWork


async def api_uow():
    uow = container.api_uow()
    async with uow:
        yield uow


class Container(containers.DeclarativeContainer):

    settings = providers.Singleton(get_settings)
    async_engine = providers.Singleton(
        create_async_engine,
        isolation_level="READ COMMITTED",
        url=ADB_URL,
        pool_pre_ping=True,
    )
    async_sessionmaker = providers.Singleton(
        async_sessionmaker,
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    uow = providers.Factory(UnitOfWork, session_factory=async_sessionmaker)
    security_service = providers.Singleton(SecurityService)


container = Container()

