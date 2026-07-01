from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_current_user, get_db
from app.main import app

# Import all models so they are registered on Base.metadata before create_all.
from app.api.user.models import User  # noqa: F401
from app.api.collection.models import Collection  # noqa: F401
from app.api.bidding_basket.models import BiddingBasket  # noqa: F401
from app.api.note.models import Note  # noqa: F401

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def as_user():
    """Override get_current_user for the duration of a test."""
    def _as_user(user_id: int):
        async def _get_current_user():
            return user_id
        app.dependency_overrides[get_current_user] = _get_current_user
    yield _as_user
    app.dependency_overrides.pop(get_current_user, None)
