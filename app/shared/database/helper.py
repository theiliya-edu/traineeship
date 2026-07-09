from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from shared.config import settings


engine = create_async_engine(settings.db.async_url)
SessionFactory = async_sessionmaker(engine)
