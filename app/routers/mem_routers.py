# import httpx

from app.routers.auth import create_access_token, create_refresh_token, verify_password, get_current_user
from app.routers.models import (Token, 
                                TokenRefresh,
                                CreateCard,
                                CreateCollection,
                                GetCardOneCard,
                                GetCollection,
                                GetListOfCards,
                                UpdateCard,
                                UpdateCollection,
                                User)
from app.database.redis import redisManager
from app.database.postgres import collectionManager, cardsManager, postgresManager

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
import logging

mem_router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mem_router.post("/token", response_model=Token)
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

@mem_router.post("/token/refresh", response_model=Token)
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

@mem_router.post('/collections/create_collection',response_class=GetCollection)
async def create_collection(collection:CreateCollection):
    try:
        new_collection = await collectionManager.create_collection(collection=collection)
        return GetCollection.model_validate(new_collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mem_router.get('/collections/get_collection',response_class=GetCollection)
async def get_collection(collection:GetCollection):
    try:
        new_collection = await collectionManager.create_collection(collection=collection)
        return GetCollection.model_validate(new_collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@mem_router.patch('/collections/update_collection',response_class=UpdateCollection)
async def update_collection(collection:UpdateCollection):
    try:
        new_collection = await collectionManager.update_collection(collection=collection)
        return UpdateCollection.model_validate(new_collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mem_router.delete('/collections/delete_collection/{collection_id}')
async def delete_collection(collection_id:int):
    try:
        collection = await collectionManager.delete_collection(collection_id=collection_id)
        return Response(status_code=200, detail='collection delete success')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@mem_router.get('/collections/all',response_class=List[GetCollection])
async def get_collection():
    try:
        collections = await collectionManager.get_collections()
        collection_lists = [GetCollection.model_validate(collection) for collection in collections]
        return collection_lists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


