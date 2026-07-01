from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from app.api.user.models import User
from app.api.user.schema import UserCreate
from typing import List
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hashed_password,
        is_superuser=user.is_superuser if user.is_superuser else False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession,
                            email: str) -> User:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def get_user(db: AsyncSession,
                   user_id: int) -> User:
    result = await db.execute(select(User).filter(User.id == int(user_id)))
    return result.scalars().first()


async def get_all_users(db: AsyncSession,
                        skip: int = 0,
                        limit: int = 10) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def change_user_email(db: AsyncSession,
                            user_id: int,
                            new_email: str,
                            current_user: User) -> User:
    user = await get_user(db, user_id)
    if not user:
        return None

    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403,
                            detail="Not authorized to change email")

    user.email = new_email
    await db.commit()
    await db.refresh(user)
    return user


async def change_user_password(db: AsyncSession,
                               user_id: int,
                               new_password: str,
                               current_user: User) -> User:
    user = await get_user(db, user_id)
    if not user:
        return None

    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403,
                            detail="Not authorized to change password")

    hashed_password = pwd_context.hash(new_password)
    user.password = hashed_password
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession,
                      user_id: int,
                      current_user: User) -> User:
    if current_user.is_superuser:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if user:
            await db.delete(user)
            await db.commit()
            return user
        else:
            return None
    else:
        raise HTTPException(status_code=403,
                            details="Not authorized to delete users")


async def top_account(db: AsyncSession, user_id: int, amount: int) -> User:
    user = await get_user(db, user_id)
    if not user:
        return None
    if amount > 0:
        user.balance += amount
        await db.commit()
        await db.refresh(user)
        return user
    raise HTTPException(status_code=400, detail="Invalid top-up amount")
