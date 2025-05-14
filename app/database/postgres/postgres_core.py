import logging

from database.postgres.models import Base, Users, Collections, Cards
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from decouple import config
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError




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
            exists = await session.execute(select(Users).filter_by(email=email))
            user_exists = exists.scalars().first() is not None
            return user_exists

    async def create_user(self, email: str, hashed_password: str):
        async with self.Session() as session:
            user = Users(email=email, hashed_password=hashed_password)
            session.add(user)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return None
            return user

    async def get_user(self, email: str):
        async with self.Session() as session:
            result = await session.execute(select(Users).filter_by(email=email))
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

    async def create_collection(self, collection):
        async with self.Session() as session:
            new_collection = Collections(
                name = collection.name,
                amount_of_cards = 0   
            )
            session.add(new_collection)
            await session.commit()
            await session.refresh(new_collection)  # Refresh to get the new ID and other defaults

            return new_collection
    
    async def get_collection(self, collection_id:int=None):
        if collection_id == None:
            return []
        
        async with self.Session() as session:
            result = await session.get(Collections, collection_id)
            # result = result.scalar_one_or_none()
            return result
        
    async def get_collections(self):
    
        async with self.Session() as session:
            result = await session.execute(
                select(Collections)
            )
            collections = result.scalars().all()
            return collections
        
    async def delete_collection(self, collection_id:int=None):
        if collection_id == None:
            return []
        
        async with self.Session() as session:
            existing = await session.get(Collections, collection_id)
            if not existing:
                return False
                
            # Perform the deletion
            result = await session.execute(
                delete(Collections)
                .where(Collections.id == collection_id)
            )
            await session.commit()
            return True
        
    async def update_collection(self, collection):
        async with self.Session() as session:
            existing_collection = await session.get(Collections, collection.id)
            
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