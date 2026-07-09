from __future__ import annotations

import datetime
from collections.abc import Sequence

from pydantic import BaseModel


class SpimexTradingResultDTO(BaseModel):
    exchange_product_id: str
    exchange_product_name: str
    delivery_basis_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_type_id: str
    volume: int | None
    total: int | None
    count: int | None
    date: datetime.date

    @classmethod
    def from_row(cls, data: Sequence[str], file_date: datetime.date) -> SpimexTradingResultDTO:
        return cls(
            exchange_product_id=data[0],
            exchange_product_name=data[1],
            delivery_basis_name=data[2],
            oil_id=data[0][:4],
            delivery_basis_id=data[0][4:7],
            delivery_type_id=data[0][-1],
            volume=int(data[3]) if data[3] else None,
            total=int(data[4]) if data[4] else None,
            count=int(data[-1]) if data[-1] else None,
            date=file_date,
        )
