from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.utils.meta_singleton import MetaSingleton

from app.config import Db


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DatabaseSingleton(metaclass=MetaSingleton):
    def __init__(self, config: Db):
        uri = URL.create(
            drivername="postgresql+asyncpg",
            username=config.postgres_user,
            password=config.postgres_password,
            host=config.db_host,
            port=config.db_port,
            database=config.postgres_db,
        )
        self.dburl = uri.render_as_string(hide_password=False)
        self.engine = None
        self.base = Base
        self.session = None

    async def init_db(self):
        self.engine = create_async_engine(self.dburl)
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)

    async def close_async(self):
        # Use on shutdown
        if self.engine is not None:
            await self.engine.dispose()

    def create_session(self) -> AsyncSession:
        session_maker = async_sessionmaker(bind=self.engine, expire_on_commit=False)
        return session_maker()
