from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.user.crud import get_user, get_user_by_email
from app.api.user.models import User
from app.db.session import get_db
from app.core.config import settings
import redis
import pytz

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

redis_client = redis.Redis(host='localhost',
                           port=6379, db=0,
                           decode_responses=True)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(pytz.UTC) + expires_delta
    else:
        expire = datetime.now(pytz.UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,
                             settings.SECRET_KEY,
                             algorithm=settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(db: AsyncSession,
                            email: str,
                            password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def blacklist_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire = payload.get("exp")
        redis_client.setex(token,
                           timedelta(seconds=expire - datetime.utcnow().
                                     timestamp()),
                           "blacklisted")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")


def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(token) == 1


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_db)) -> User:
    if is_token_blacklisted(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has been revoked")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"JWT Payload: {payload}")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(db, user_id)
    if user is None:
        raise credentials_exception
    return user
