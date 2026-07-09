from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from ..book import Book
    from ..order import Order


class OrderBookAssociation(Base):
    __tablename__ = "order_book_association"
    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "step_id",
            name="unq_order_book_association_order_id_book_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column(default=1)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))

    order: Mapped[Order] = relationship(back_populates="books_details")
    book: Mapped[Book] = relationship(back_populates="orders_details")
