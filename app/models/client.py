from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .city import City
    from .order import Order


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    email: Mapped[str]

    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))

    city: Mapped[City] = relationship(back_populates="clients")
    orders: Mapped[list[Order]] = relationship(back_populates="client")
