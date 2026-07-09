from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .associations import OrderBookAssociation, OrderStepAssociation
    from .client import Client


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str | None]

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))

    client: Mapped[Client] = relationship(back_populates="orders")

    books_details: Mapped[list[OrderBookAssociation]] = relationship(back_populates="order")
    steps_details: Mapped[list[OrderStepAssociation]] = relationship(back_populates="order")
