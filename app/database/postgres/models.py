import datetime
from typing import Annotated, List
from sqlalchemy import ForeignKey, Integer, String,Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base


intpk = Annotated[int, mapped_column(primary_key=True)]

str_256 = Annotated[str, 256]

class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256)
    }

    repr_cols_num = 3
    repr_cols = tuple()
    
    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

card_collection_association = Table(
    'card_collection', Base.metadata,
    Column('card_id', Integer, ForeignKey('cards.id'), primary_key=True),
    Column('collection_id', Integer, ForeignKey('collections.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    email: Mapped[str] = mapped_column(String(256))
    hashed_password: Mapped[str] = mapped_column(String(256))

    repr_cols_num = 2
    repr_cols = ("email",)

    collections: Mapped[List["Collections"]] = relationship(
        "Collections", back_populates="user"
    )


class Collections(Base):
    __tablename__ = 'collections'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), unique=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
    repr_cols_num = 2
    repr_cols = ("name", "amount_of_cards")

    cards: Mapped[List["Cards"]] = relationship(
        "Cards", secondary=card_collection_association, back_populates="collections"
    )

    user: Mapped["User "] = relationship(
        "User ", back_populates="collections"
    )


class Cards(Base):
    __tablename__ = 'cards'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    text: Mapped[str] = mapped_column(String)

    collections: Mapped[List[Collections]] = relationship(
        "Collections", secondary=card_collection_association, back_populates="cards"
    )
