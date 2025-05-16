import logging

from database.postgres.models import Base, CollectionCards, User, Collections, Cards, CollectionCards
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from decouple import config
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from typing import Optional
from sqlalchemy.orm import selectinload


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PosgtresCore:
    def __init__(self,
                 db_user: str = config('POSTGRES_USER'),
                 db_pwd: str = config('POSTGRES_PASSWORD'),
                 db_host: str = config('POSTGRES_HOST'),
                 db_port: str = config('POSTGRES_PORT'),
                 db_name: str = config('POSTGRES_DB')):

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
                # Обновляем объект user, чтобы получить id
                await session.refresh(user)
                logger.info(
                    f"Пользователь создан: {user.email} с ID: {user.id}")
                return user  # Возвращаем объект user с id
            except IntegrityError as e:
                await session.rollback()
                # Логируем оригинальную ошибку
                logger.error(f"Ошибка при создании пользователя: {e.orig}")
                return None
            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Неизвестная ошибка при создании пользователя: {e}")
                return None

    async def get_user(self, email: str):
        async with self.Session() as session:
            result = await session.execute(select(User).filter_by(email=email))
            user = result.scalars().first()
            return user

    async def create_default_collection(self, user_id: int = None):
        async with self.Session() as session:
            new_collection = Collections(
                name='Все карточки',
                # amount_of_cards = 0,
                user_id=user_id
            )
            session.add(new_collection)
            await session.commit()

            return new_collection

    async def init_admin_user(self):
        email = config('ADMIN_EMAIL')
        if not await self.check_user_exists(email=email):
            password = config('ADMIN_PASSWORD')
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(password)

            user = await self.create_user(email, hashed_password)

            if user is None:
                raise Exception("Не удалось создать администратора.")

            # Создаем коллекцию по умолчанию
            await self.create_default_collection(user_id=user.id)

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

    async def count_amount(self, collection_id):
        async with self.Session() as session:  # Предполагается, что self.Session() - это асинхронная сессия
            # Формируем запрос для подсчета количества карт в коллекции с заданным collection_id
            stmt = select(Cards).where(
                Cards.collection_cards.any(
                    CollectionCards.collection_id == collection_id
                ))
            result = await session.execute(stmt)
            count = len(result.scalars().all())  # Получаем количество записей
            return int(count)

    async def create_collection(self, collection, user_id):
        async with self.Session() as session:
            new_collection = Collections(
                name=collection.name,
                # amount_of_cards = 0,
                user_id=user_id
            )
            session.add(new_collection)
            await session.commit()
            # Refresh to get the new ID and other defaults
            await session.refresh(new_collection)
            if new_collection:
                new_collection.amount_of_cards = 0
                return new_collection
            else:
                return {}

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
            collection = result.scalar_one_or_none()
            if collection is not None:
                collection.amount_of_cards = await self.count_amount(collection_id=collection_id)
            return collection

    async def get_collections_with_cards(self, user_id: int, limit_cards: int = 5):
        async with self.Session() as session:
            # Сначала получаем все коллекции пользователя
            collections_stmt = select(Collections).where(
                Collections.user_id == user_id)
            collections_result = await session.execute(collections_stmt)
            user_collections = collections_result.scalars().all()

            if not user_collections:
                return []

            # Создаем базовую структуру для всех коллекций с пустыми картами
            collections_map = {}
            for collection in user_collections:
                # Получаем количество карт в коллекции
                count_stmt = select(func.count()).select_from(
                    Cards).where(Cards.collection_cards.any(
                        CollectionCards.collection_id == collection.id
                    ))
                count_result = await session.execute(count_stmt)
                amount_of_cards = count_result.scalar_one()

                collections_map[collection.id] = {
                    "id": collection.id,
                    "name": collection.name,
                    "amount_of_cards": amount_of_cards,
                    "cards": []
                }

            # Теперь получаем карты с ограничением по количеству для каждой коллекции
            # Создаем подзапрос для нумерации карточек в каждой коллекции
            numbered_cards = (
                select(
                    CollectionCards,
                    func.row_number().over(
                        partition_by=CollectionCards.collection_id,
                        order_by=CollectionCards.card_id  # или другой критерий сортировки
                    ).label('row_num')
                )
                .subquery()
            )

            # Основной запрос для получения коллекций с ограниченным количеством карточек
            stmt = (
                select(Collections)
                .join(
                    numbered_cards,
                    numbered_cards.c.collection_id == Collections.id
                )
                .filter(
                    Collections.user_id == user_id,
                    numbered_cards.c.row_num <= limit_cards
                )
                .options(
                    selectinload(Collections.collection_cards.and_(
                        numbered_cards.c.row_num <= limit_cards
                    )).selectinload(CollectionCards.card)
                )
                .distinct()
            )

            result = (await session.execute(stmt)).scalars().all()

            # Добавляем карты в соответствующие коллекции
            for collection in result:
                print(collection)
                if collection.id in collections_map:
                    for card in collection.collection_cards:
                        print(card)
                        collections_map[collection.id]["cards"].append(
                            card.card)

            return list(collections_map.values())

    async def delete_collection(self, collection_id: int = None, user_id: int = None):
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
            existing_collection = (await session.execute(
                select(Collections)
                .where(Collections.id == collection.id,
                       Collections.user_id == user_id)
            )).scalars().first()

            if existing_collection is None:
                raise ValueError("Collection not found")
            if collection.name is not None:
                existing_collection.name = collection.name

            # if collection.amount_of_cards is not None:
            #     existing_collection.amount_of_cards = collection.amount_of_cards

            await session.commit()
            await session.refresh(existing_collection)
            existing_collection.amount_of_cards = await self.count_amount(collection_id=collection.id)
            return existing_collection


class CardsManager(CollectionManager):
    async def create_card(self, card):
        async with self.Session() as session:
            new_card = Cards(
                text=card.text,
            )
            session.add(new_card)
            await session.flush()

            for id_collection in card.collection_ids:
                new_collection_card = CollectionCards(
                    collection_id=int(id_collection),
                    card_id=new_card.id
                )
                session.add(new_collection_card)

            await session.commit()
            await session.refresh(new_card)
            return new_card

    async def get_card(self, card_id: int):
        async with self.Session() as session:
            result = await session.get(Cards, card_id)
            if result:
                result.collection_ids = [collection_card.collection_id for collection_card in result.collection_cards]

            return result

    async def update_card(self, card):
        async with self.Session() as session:
            exisiting_card = await session.get(Cards, card.id)

            if exisiting_card is None:
                raise ValueError("Card not found")

            if card.text is not None:
                exisiting_card.text = card.text

            if card.collection_ids is not None:
                query = select(CollectionCards).where(
                    CollectionCards.card_id == card.id
                )

                col_cards = (await session.execute(query)).scalars().all()

                for col_card in col_cards:
                    await session.delete(col_card)

                for id_collection in card.collection_ids:
                    new_collection_card = CollectionCards(
                        collection_id=int(id_collection),
                        card_id=card.id
                    )
                    session.add(new_collection_card)

            await session.commit()
            await session.refresh(exisiting_card)
            exisiting_card.collection_ids = card.collection_ids
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

    async def get_cards(self, collection_id: int = None):
        if collection_id is None:
            return []

        async with self.Session() as session:
            result = await session.execute(
                select(Cards).where(Cards.collection_cards.any(
                    CollectionCards.collection_id == collection_id
                )).options(
                    selectinload(Cards.collection_cards)
                )
            )
            result = result.scalars().all()

            for r in result:
                r.collection_ids = [
                    c.collection_id for c in r.collection_cards]
            return result

    async def random_card(self, user_id: int = None, collection_id=None):
        if user_id is None:
            return {}

        async with self.Session() as session:
            if collection_id is None:
                stmt = (
                    select(Cards)
                    .filter(
                        Cards.collection_cards.any(
                            CollectionCards.collection_id == Collections.id),
                        (Collections.user_id == user_id)
                    )
                    .order_by(func.random())
                    .limit(1)
                )
            else:
                stmt = (
                    select(Cards)
                    .where(Collections.user_id == user_id)
                    .order_by(func.random())
                    .limit(1)
                )

            result = await session.execute(stmt)
            random_card = result.scalars().first()
            if random_card:
                random_card.collection_ids = [collection_card.collection_id for collection_card in result.collection_cards]

            return random_card

    async def get_all_cards(self, user_id: int = None):
        if user_id is None:
            return []

        async with self.Session() as session:
            stmt = (
                select(Cards)
                .where(Cards.collection_cards.any(
                    CollectionCards.collection.has(
                        Collections.user_id == user_id
                    )
                ))
            )
            query = await session.execute(stmt)

            result = query.scalars().all()
            return result
