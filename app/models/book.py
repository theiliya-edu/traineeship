from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .associations import OrderBookAssociation
    from .author import Author
    from .genre import Genre


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    price: Mapped[Decimal]
    amount: Mapped[int]

    authors: Mapped[list[Author]] = relationship(secondary="book_author_association", back_populates="books")
    genres: Mapped[list[Genre]] = relationship(secondary="book_genre_association", back_populates="books")

    orders_details: Mapped[list[OrderBookAssociation]] = relationship(back_populates="book")
