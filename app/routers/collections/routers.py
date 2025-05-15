# import httpx

from routers.collections.models import (CreateCollection,
                                        GetCollection,
                                        GetListOfCards,
                                        UpdateCollection)
from routers.users.models import User
from routers.users.auth import get_current_user
from database.postgres import collectionManager, cardsManager

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import logging

collection_router = APIRouter(prefix='/collections', tags=['collections'])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@collection_router.post('/create_collection',response_model=GetCollection)
async def create_collection(collection:CreateCollection, current_user: User = Depends(get_current_user)):
    try:
        user_id = current_user.id
        new_collection = await collectionManager.create_collection(collection=collection, user_id=user_id)
        return GetCollection.model_validate(new_collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@collection_router.patch('/update_collection',response_model=UpdateCollection)
async def update_collection(collection:UpdateCollection, current_user: User = Depends(get_current_user)):
    try:
        new_collection = await collectionManager.update_collection(collection=collection)
        return UpdateCollection.model_validate(new_collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@collection_router.delete('/{collection_id}')
async def delete_collection(collection_id:int, current_user: User = Depends(get_current_user)):
    try:
        collection = await collectionManager.delete_collection(collection_id=collection_id)
        return JSONResponse(status_code=200, content={'message':'collection delete success'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@collection_router.get('/all', response_model=List[GetCollection])
async def get_all_collections(current_user: User = Depends(get_current_user)):
    try:
        collections = await collectionManager.get_collections()
        collection_lists = [GetCollection.model_validate(collection) for collection in collections]
        return collection_lists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@collection_router.get('/{collection_id}/cards', response_model=List[GetListOfCards])
async def get_collection_cards(collection_id:int, current_user: User = Depends(get_current_user)):
    try:
        cards = await cardsManager.get_cards(collection_id=collection_id)
        cards_lists = [GetListOfCards.model_validate(card) for card in cards]
        return cards_lists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@collection_router.get('/{collection_id}',response_model=GetCollection)
async def get_collection(collection_id:int, current_user: User = Depends(get_current_user)):
    try:
        new_collection = await collectionManager.get_user_collection(collection_id=collection_id)
        return GetCollection.model_validate(new_collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
