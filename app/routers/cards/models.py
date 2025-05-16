from datetime import datetime, date
from pydantic import BaseModel, UUID4
from typing import Union, Optional


class CreateCard(BaseModel):
    collection_ids: list[int]
    text: str

    class Config:
        from_attributes = True
        orm_mode = True


class GetListOfCards(BaseModel):
    id: int
    collection_ids: list[int]
    text: str

    class Config:
        from_attributes = True
        orm_mode = True


class GetCardOneCard(BaseModel):
    id: int
    text: str
    # collection_ids: list[int]


    class Config:
        from_attributes = True
        orm_mode = True


class UpdateCard(BaseModel):
    id: int
    collection_ids: Optional[list[int]] = None
    text: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True


class DeleteCard(BaseModel):
    id: int

    class Config:
        from_attributes = True
        orm_mode = True


class RandomCard(BaseModel):
    collection_id: Optional[int] = None
