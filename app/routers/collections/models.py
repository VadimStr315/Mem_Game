from datetime import datetime, date
from pydantic import BaseModel, UUID4
from typing import Union, Optional


class CreateCollection(BaseModel):
    id:int
    name:str


class GetCollection(BaseModel):
    id: int
    name:str
    amount_of_cards: int


class UpdateCollection(BaseModel):
    id: int
    name:Optional[str] = None
    amount_of_cards: Optional[int] = None


class DeleteCollection(BaseModel):
    id:int


class GetListOfCards(BaseModel):
    id:int
    collection_id:int
    text:str
