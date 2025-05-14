from database.postgres.models import Users
from database.postgres import postgresManager

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from decouple import config

# Секретный ключ и алгоритм
SECRET_AUTH_KEY = config('SECRET_AUTH_KEY')
ALGORITHM = config('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = config('REFRESH_TOKEN_EXPIRE_DAYS', default=30)

# Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция для хеширования пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Функция для проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Функция для создания JWT токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_AUTH_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для создания refresh токена
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_AUTH_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для получения текущего пользователя
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_AUTH_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await postgresManager.get_user(email)
    if user is None:
        raise credentials_exception  # Обработка случая, когда пользователь не найден
    return user