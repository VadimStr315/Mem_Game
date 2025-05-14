# import httpx

from routers.collections.models import (CreateCollection,
                                        GetCollection,
                                        GetListOfCards,
                                        UpdateCollection)
from database.postgres import collectionManager, cardsManager

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
import logging

collection_router = APIRouter(prefix='/collections', tags=['collections'])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@collection_router.post('/create_collection',response_model=GetCollection)
async def create_collection(collection:CreateCollection):
    try:
        new_collection = await collectionManager.create_collection(collection=collection)
        return GetCollection.model_validate(new_collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@collection_router.get('/get_collection',response_model=GetCollection)
async def get_collection(collection:GetCollection):
    try:
        new_collection = await collectionManager.create_collection(collection=collection)
        return GetCollection.model_validate(new_collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@collection_router.patch('/update_collection',response_model=UpdateCollection)
async def update_collection(collection:UpdateCollection):
    try:
        new_collection = await collectionManager.update_collection(collection=collection)
        return UpdateCollection.model_validate(new_collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@collection_router.delete('/delete_collection/{collection_id}')
async def delete_collection(collection_id:int):
    try:
        collection = await collectionManager.delete_collection(collection_id=collection_id)
        return Response(status_code=200, detail='collection delete success')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@collection_router.get('/all',response_model=List[GetCollection])
async def get_collections():
    try:
        collections = await collectionManager.get_collections()
        collection_lists = [GetCollection.model_validate(collection) for collection in collections]
        return collection_lists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@collection_router.get('/{collection_id}/cards', response_model=List[GetListOfCards])
async def get_collection_cards(collection_id:int):
    try:
        cards = await cardsManager.get_cards(collection_id=collection_id)
        cards_lists = [GetListOfCards.model_validate(card) for card in cards]
        return cards_lists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
