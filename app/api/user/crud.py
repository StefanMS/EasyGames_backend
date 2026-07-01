from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from app.api.user.models import User
from app.api.user.schema import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(db: AsyncSession, email: str) -> User:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def get_user(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db: AsyncSession, email: str,
                            password: str) -> User:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
