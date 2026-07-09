from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .associations import OrderStepAssociation


class Step(Base):
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    orders_details: Mapped[list[OrderStepAssociation]] = relationship(back_populates="step")
