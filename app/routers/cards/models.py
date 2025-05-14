from datetime import datetime, date
from pydantic import BaseModel, UUID4
from typing import Union, Optional

class CreateCard(BaseModel):
    collecton_id: int
    text:str

class GetListOfCards(BaseModel):
    id:int
    collection_id:int
    text:str

class GetCardOneCard(BaseModel):
    text:str


class UpdateCard(BaseModel):
    id:int
    collection_id: Optional[int] = None
    text:Optional[str] = None


class DeleteCard(BaseModel):
    id:int

