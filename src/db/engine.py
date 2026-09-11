from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.database_settings import database_settings

engine = create_async_engine(database_settings.database_dsn.encoded_string())
session_maker = async_sessionmaker(engine, expire_on_commit=False)
