'''
Session module for database
'''
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import AsyncGenerator

engine = create_async_engine(settings.DATABASE_URL,
                             echo=True, 
                             future=True)
print(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine,
                            class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
