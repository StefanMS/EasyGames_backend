from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.api.user import crud
from app.api.user.schema import UserCreate, UserResponse

from app.db.session import get_db

router = APIRouter()


@router.post("/login", response_model=UserResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(),
                     db: AsyncSession = Depends(get_db)):
    user = await crud.authenticate_user(db, form_data.username,
                                        form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return user


@router.post("/sign-up", response_model=UserResponse)
async def sign_up_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await crud.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    created_user = await crud.create_user(db, user)
    return created_user


@router.post("/logout")
async def logout_user():
    # Implement token invalidation or session logout logic here
    return {"msg": "User logged out successfully"}
