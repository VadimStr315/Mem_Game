# import httpx

from routers.users.auth import create_access_token, create_refresh_token, verify_password, get_current_user
from routers.users.models import (Token, 
                                TokenRefresh,
                                User)
from database.redis import redisManager
from database.postgres import collectionManager, cardsManager, postgresManager

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
import logging


users_router = APIRouter(prefix='/users', tags=['users'])



@users_router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await postgresManager.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    await redisManager.set(f"refresh_token:{user.email}", refresh_token, expire=12 * 60 * 60)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@users_router.post("/token/refresh", response_model=Token)
async def refresh_token(token: TokenRefresh):
    stored_refresh_token = await redisManager.get(f"refresh_token:{token.refresh_token}")
    if not stored_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = token.refresh_token.split(":")[1]
    access_token = create_access_token(data={"sub": email})
    new_refresh_token = create_refresh_token(data={"sub": email})

    await redisManager.set(f"refresh_token:{email}", new_refresh_token, expire=12 * 60 * 60)

    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}