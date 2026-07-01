'''
Initializing module for admin
'''
from app.api.user.crud import create_user
from app.api.user.schema import UserCreate
from app.api.user.models import User
from app.core.config import settings
from sqlalchemy.future import select
from app.db.session import get_db


async def create_superuser():
    async for session in get_db():
        result = await session.execute(
            select(User).where(User.email == settings.ADMIN_USER_EMAIL)
        )
        admin_user = result.scalar()
        if not admin_user:
            admin_user_data = UserCreate(
                email=settings.ADMIN_USER_EMAIL,
                password=settings.ADMIN_USER_PASSWORD,
                first_name=settings.ADMIN_USER_FIRST_NAME,
                last_name=settings.ADMIN_USER_LAST_NAME,
                is_superuser=True
            )
            await create_user(db=session, user=admin_user_data)
