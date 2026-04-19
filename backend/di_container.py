from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cfg import ADB_URL
from src.app.services.auth_session import AuthSessionService
from src.app.services.mail import MailService
from src.app.services.security import SecurityService
from src.modules.shared.unit_of_work import UnitOfWork


async def api_uow():
    uow = container.uow()
    async with uow:
        yield uow


class Container(containers.DeclarativeContainer):
    api_engine = providers.Singleton(
        create_async_engine,
        isolation_level="READ COMMITTED",
        url=ADB_URL,
        pool_pre_ping=True,
    )
    api_sessionmaker = providers.Singleton(
        async_sessionmaker,
        bind=api_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = providers.Factory(api_sessionmaker())
    uow = providers.Factory(UnitOfWork, session=session)
    security_service = providers.Singleton(SecurityService)
    mail_service = providers.Singleton(MailService)
    auth_session_service = providers.Singleton(AuthSessionService, sec=security_service)


container = Container()
