'''
Session module for database
'''
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine,
                            class_=AsyncSession)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def get_current_user() -> int:
    # Replace with your actual authentication logic
    # to get the current user's ID
    return 1  # Dummy user ID for illustration
