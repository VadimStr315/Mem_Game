import datetime
from typing import Annotated, List
from sqlalchemy import ForeignKey, Integer, String, Date, Boolean, Float, UniqueConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.orm import validates


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


class Users(Base):
    __tablename__ = 'users'

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    
    name:Mapped[str] = mapped_column(String(100), nullable=True)
    surname: Mapped[str] = mapped_column(String(100), nullable=True)

    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))


class Collections(Base):
    __tablename__ = 'collections'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name:  Mapped[str] = mapped_column(String(255))
    amount_of_cards:  Mapped[int] = mapped_column(Integer)


    repr_cols_num = 2
    repr_cols = ("name", "amount_of_cards")

    cards: Mapped[List["Cards"]] = relationship(
    "Cards", back_populates="collection")


class Cards(Base):
    __tablename__ = 'cards'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    text:  Mapped[str] = mapped_column(String)
    collection_id: Mapped[int] = mapped_column(
        ForeignKey('collections.id', ondelete='CASCADE'))
    collection: Mapped[Collections] = relationship(
        'Collections', back_populates='cards')