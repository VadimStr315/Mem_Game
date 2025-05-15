import logging

from database.postgres.models import Base, User, Collections, Cards
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from decouple import config
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from typing import Optional




class PosgtresCore:
    def __init__(self, 
                 db_user:str = config('POSTGRES_USER'),
                 db_pwd:str = config('POSTGRES_PASSWORD'),
                 db_host:str = config('POSTGRES_HOST'),
                 db_port:str = config('POSTGRES_PORT'),
                 db_name:str = config('POSTGRES_DB')):
        
        self.db_user = db_user
        self.db_pwd = db_pwd
        self.db_host = db_host
        self.db_port = db_port 
        self.db_name = db_name
        self.db_url = f"postgresql+asyncpg://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}"
        self.engine = None
        self.Session = None

        try:
            self.engine = create_async_engine(self.db_url, echo=True)
            self.Session = async_sessionmaker(self.engine)
        except Exception as e:
            raise ConnectionError(f'Cannot connect to database: {e}')

    async def check_user_exists(self, email: str) -> bool:
        async with self.Session() as session:
            exists = await session.execute(select(User).filter_by(email=email))
            user_exists = exists.scalars().first() is not None
            return user_exists

    async def create_user(self, email: str, hashed_password: str):
        async with self.Session() as session:
            user = User(email=email, hashed_password=hashed_password)
            session.add(user)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return None
            return user

    async def get_user(self, email: str):
        async with self.Session() as session:
            result = await session.execute(select(User).filter_by(email=email))
            user = result.scalars().first()
            return user
        
    async def init_admin_user(self):
        email = config('ADMIN_EMAIL')
        if not await self.check_user_exists(email=email):
            password = config('ADMIN_PASSWORD')
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(password)
            await self.create_user(email, hashed_password)

    async def init_db(self):
        """Initialize the database and create tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            await self.init_admin_user()
        except Exception as e:
            raise

    async def close(self):
        """Close the database connection."""
        await self.engine.dispose()


class CollectionManager(PosgtresCore):

    async def create_collection(self, collection, user_id):
        async with self.Session() as session:
            new_collection = Collections(
                name = collection.name,
                amount_of_cards = 0,
                user_id=user_id   
            )
            session.add(new_collection)
            await session.commit()
            await session.refresh(new_collection)  # Refresh to get the new ID and other defaults

            return new_collection
    
    async def get_user_collection(
        self, 
        collection_id: int, 
        user_id: int):
        async with self.Session() as session:
            result = await session.execute(
                select(Collections)
                .where(
                    Collections.id == collection_id,
                    Collections.user_id == user_id
                )
            )
            return result.scalar_one_or_none()
        
    async def get_collections_with_cards(self, user_id: int, limit_cards: int = 5):
        async with self.Session() as session:
            # Создаем подзапрос для карточек с нумерацией внутри коллекции
            numbered_cards = (
                select(
                    Cards,
                    func.row_number().over(
                        partition_by=Cards.collection_id,
                        order_by=Cards.id
                    ).label('row_num')
                )
                .subquery()
            )

            # Основной запрос с фильтрацией по номеру строки
            stmt = (
                select(Collections, Cards)
                .join(numbered_cards, Collections.id == numbered_cards.c.collection_id)
                .where(
                    (Collections.user_id == user_id) &
                    (numbered_cards.c.row_num <= limit_cards)
                )
                .order_by(Collections.id, numbered_cards.c.row_num)
            )

            result = await session.execute(stmt)
            
            # Группируем результаты по коллекциям
            collections_map = {}
            for collection, card in result:
                if collection.id not in collections_map:
                    collections_map[collection.id] = {
                        "id": collection.id,
                        "name": collection.name,
                        "amount_of_cards": collection.amount_of_cards,
                        "cards": []
                    }
                collections_map[collection.id]["cards"].append(card)
            
            return list(collections_map.values())
        
    async def delete_collection(self, collection_id:int=None, user_id:int=None):
        if collection_id == None:
            return []
        
        async with self.Session() as session:
            existing = await session.execute(
                select(Collections)
                .where(Collections.id == collection_id,
                       Collections.user_id == user_id) 
            )
            if not existing:
                return False
                
            # Perform the deletion
            result = await session.execute(
                delete(Collections)
                .where(Collections.id == collection_id,
                       Collections.user_id == user_id)
            )
            await session.commit()
            return True
        
    async def update_collection(self, collection, user_id):
        async with self.Session() as session:
            existing_collection  = await session.execute(
                select(Collections)
                .where(Collections.id == collection.id,
                       Collections.user_id == user_id) 
            )
            
            if existing_collection is None:
                raise ValueError("Collection not found")
            if collection.name is not None:
                existing_collection.name = collection.name
            
            if collection.amount_of_cards is not None:
                existing_collection.amount_of_cards = collection.amount_of_cards
            
            await session.commit()
            await session.refresh(existing_collection)
            return existing_collection


class CardsManager(PosgtresCore):
    async def create_card(self, card:Cards):
        async with self.Session() as session:
            new_card = Cards(
                text = card.text,
                collection_id = card.collection_id,
            )

            session.add(new_card)
            await session.commit()
            await session.refresh(new_card)

            return new_card
        
    async def get_card(self,card_id):
        async with self.Session() as session:
            result = await session.get(Cards, card_id)
            return result
        
    async def update_card(self, card):
        async with self.Session() as session:
            exisiting_card = await session.get(Cards, card.id)

            if exisiting_card is None:
                raise ValueError("Card not found")
            
            if card.text is not None:
                exisiting_card.text = card.text

            if card.collection_id is not None:
                exisiting_card.collection_id = card.collection_id
            
            await session.commit()
            await session.refresh(exisiting_card)
            return exisiting_card
        
    async def delete_card(self, card_id):
        if card_id == None:
            return []
        
        async with self.Session() as session:
            existing = await session.get(Cards, card_id)
            if not existing:
                return False
                
            # Perform the deletion
            result = await session.execute(
                delete(Cards)
                .where(Cards.id == card_id)
            )
            await session.commit()
            return True
        
    async def get_cards(self, collection_id:int = None):
        if collection_id is None:
            return []
        
        async with self.Session() as session:
            result = await session.execute(
                select(Cards).where(Cards.collection_id == collection_id)
            )
            result = result.all()
            return result
        
    async def random_card(self, user_id:int = None, collection_id = None):
        if user_id is None:
            return {}
        
        async with self.Session() as session:
            if collection_id is None:
                stmt = (
                    select(Cards)
                    .join(Collections, Cards.collection_id == Collections.id)
                    .where(
                        (Cards.collection_id == collection_id) &
                        (Collections.user_id == user_id)
                    )
                    .order_by(func.random())
                    .limit(1)
                )
            else:
                stmt = (
                    select(Cards)
                    .join(Collections, Cards.collection_id == Collections.id)
                    .where(Collections.user_id == user_id)
                    .order_by(func.random())
                    .limit(1)
                )

            result = await session.execute(stmt)
            random_card = result.scalars().first()

            return random_card
