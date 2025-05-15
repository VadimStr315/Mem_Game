from datetime import datetime, date
from pydantic import BaseModel, UUID4
from typing import Union, Optional, List


class CreateCollection(BaseModel):
    name:str


class CardResponse(BaseModel):
    id: int
    text: str

    class Config:
        from_attributes = True  # Ранее orm_mode=True в Pydantic v1

class CollectionWithCardsResponse(BaseModel):
    id: int
    name: str
    amount_of_cards: int
    cards: List[CardResponse]  # Добавляем поле для карточек

    class Config:
        from_attributes = True

class GetCollection(BaseModel):
    id: int
    name:str
    amount_of_cards: int

    class Config:
        orm_mode = True
        from_attributes = True


class UpdateCollection(BaseModel):
    id: int
    name:Optional[str] = None
    amount_of_cards: Optional[int] = None

    class Config:
        from_attributes = True
        orm_mode = True


class DeleteCollection(BaseModel):
    id:int

    class Config:
        from_attributes = True
        orm_mode = True


class GetListOfCards(BaseModel):
    id:int
    collection_id:int
    text:str

    class Config:
        from_attributes = True
        orm_mode = True