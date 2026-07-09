from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from ..order import Order
    from ..step import Step


class OrderStepAssociation(Base):
    __tablename__ = "order_step_association"
    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "step_id",
            name="unq_order_step_association_order_id_step_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[datetime] = mapped_column(default=datetime.now(UTC), server_default=func.now())
    end_date: Mapped[datetime | None] = mapped_column(default=None)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    step_id: Mapped[int] = mapped_column(ForeignKey("steps.id"))

    order: Mapped[Order] = relationship(back_populates="steps_details")
    step: Mapped[Step] = relationship(back_populates="orders_details")
