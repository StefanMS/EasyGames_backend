from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import timedelta
from app.api.user.crud import (
    create_user,
    get_user_by_email,
    get_user,
    get_all_users,
    change_user_email,
    change_user_password,
    top_account,
    delete_user
)
from app.api.user.schema import UserCreate, UserResponse, TokenResponse
from app.api.user.models import User
from app.db.session import get_db
from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    blacklist_token,
    oauth2_scheme)
from app.core.config import settings
from app.logs.logs import logging


router = APIRouter()


@router.post("/login", response_model=TokenResponse,
             tags=["User"])
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(),
                     db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db,
                                   form_data.username,
                                   form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token_expires = timedelta(
                            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)},
                                       expires_delta=access_token_expires)
    logging.info(f"User {user.id} logged in")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/sign-up", response_model=UserResponse,
             tags=["User"])
async def sign_up_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    created_user = await create_user(db, user)
    logging.info(f"User {created_user.id} created")
    return created_user


@router.get("/users/{user_id}", response_model=Optional[UserResponse],
            tags=["User"])
async def get_user_by_id_route(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=403,
                            detail="Not authorized to access this user")

    user = await get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404,
                            detail="User not found")
    return user


@router.get("/users/email/{email}", response_model=Optional[UserResponse],
            tags=["User"])
async def get_user_by_email_route(
    email: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await get_user_by_email(db=db, email=email)
    if not user:
        raise HTTPException(status_code=404,
                            detail="User not found")
    if not current_user.is_superuser and current_user.id != user.id:
        raise HTTPException(status_code=403,
                            detail="Not authorized to access this user")
    return user


@router.get("/users/", response_model=List[UserResponse],
            tags=["User"])
async def get_all_users_route(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403,
                            detail="Not authorized to access all users")
    users = await get_all_users(db=db, skip=skip, limit=limit)
    return users


@router.put("/users/{user_id}/change-email", response_model=UserResponse,
            tags=["User"])
async def change_email_route(
    user_id: int,
    new_email: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await change_user_email(db=db,
                                   user_id=user_id,
                                   new_email=new_email,
                                   current_user=current_user)
    logging.info(f"User {user.id} email changed to {new_email}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}/change-password", response_model=UserResponse,
            tags=["User"])
async def change_password_route(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await change_user_password(db=db,
                                      user_id=user_id,
                                      new_password=new_password,
                                      current_user=current_user)
    logging.info(f"User {user.id} password changed")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users/{user_id}/top-up/{amount}", response_model=UserResponse,
             tags=["User"])
async def top_up_balance_route(
    user_id: int,
    amount: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403,
                            detail="Not authorized to top up this account")

    user = await top_account(db=db, user_id=user_id, amount=amount)
    logging.info(f"User {user.id} top up by {amount}")
    if not user:
        raise HTTPException(status_code=404,
                            detail="User not found")
    return user


async def logout_user(token: str = Depends(oauth2_scheme)):
    """
    Invalidate the current JWT token by blacklisting it.
    """
    blacklist_token(token)
    return {"msg": "User logged out successfully"}


@router.delete("/users/{user_id}/delete", response_model=UserResponse,
               tags=["User"])
async def delete_user_route(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.is_superuser:
        user = await delete_user(db=db,
                                 user_id=user_id,
                                 current_user=current_user)
        if not user:
            raise HTTPException(status_code=404,
                                detail="User not found")
        return user
    else:
        raise HTTPException(status_code=403,
                            detail="Not authorized to delete users")
