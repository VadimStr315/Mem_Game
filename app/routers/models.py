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


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str


class UserInDB(User):
    hashed_password: str

