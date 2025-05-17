from routers.cards.models import (CreateCard,
                                  GetCardOneCard,
                                  GetListOfCards,
                                  UpdateCard,
                                  RandomCard)
from database.redis import redisManager
from database.postgres import collectionManager, cardsManager, postgresManager
from routers.users.models import User
from routers.users.auth import get_current_user
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from fastapi.security import OAuth2PasswordRequestForm
import logging

cards_router = APIRouter(prefix='/card', tags=['cards'])


@cards_router.post('/create', response_model=GetCardOneCard)
async def create_card(card: CreateCard, current_user: User = Depends(get_current_user)):
    try:
        new_card = await cardsManager.create_card(card=card)
        return GetCardOneCard.model_validate(new_card)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cards_router.patch('/update', response_model=UpdateCard)
async def update_card(card: UpdateCard, current_user: User = Depends(get_current_user)):
    try:
        updated_card = await cardsManager.update_card(card=card)
        return UpdateCard.model_validate(updated_card)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cards_router.delete('/{card_id}')
async def delete_card(card_id: int, current_user: User = Depends(get_current_user)):
    try:
        del_card = await cardsManager.delete_card(card_id=card_id)
        if del_card:
            return JSONResponse(status_code=200, content='Card deleted sucess')
        else:
            return JSONResponse(status_code=404, content='Card not found')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cards_router.get('/{card_id}', response_model=GetCardOneCard)
async def get_card(card_id: int, current_user: User = Depends(get_current_user)):
    try:
        card = await cardsManager.get_card(card_id=card_id)
        return GetCardOneCard.model_validate(card)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cards_router.get('/random_card/{collection_id}', response_model=GetCardOneCard)
async def get_random_card(collection_id: int, current_user: User = Depends(get_current_user)):
    try:
        user_id = current_user.id
        card = await cardsManager.random_card(user_id=user_id, collection_id=collection_id)

        return GetCardOneCard.model_validate(card)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cards_router.get('/all/', response_model=list[GetCardOneCard])
async def get_all_cards(current_user: User = Depends(get_current_user)):
    try:
        user_id = current_user.id
        cards = await cardsManager.get_all_cards(user_id=user_id)
        cards = [GetCardOneCard.model_validate(card) for card in cards]
        return cards
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
