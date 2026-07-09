import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.models import SpimexTradingResult


class TradingResultRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_last_trading_dates(self, limit: int) -> list[datetime.date]:
        stmt = select(SpimexTradingResult.date).distinct().order_by(SpimexTradingResult.date.desc()).limit(limit)
        raw = await self.session.execute(stmt)

        return list(raw.scalars().all())

    async def get_dynamics(
        self,
        oil_id: str,
        delivery_type_id: str,
        delivery_basis_id: str,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> list[SpimexTradingResult]:
        stmt = (
            select(SpimexTradingResult)
            .where(SpimexTradingResult.date.between(start_date, end_date))
            .where(SpimexTradingResult.oil_id == oil_id)
            .where(SpimexTradingResult.delivery_type_id == delivery_type_id)
            .where(SpimexTradingResult.delivery_basis_id == delivery_basis_id)
            .order_by(SpimexTradingResult.date.desc())
        )

        raw = await self.session.execute(stmt)
        return list(raw.scalars().all())

    async def get_trading_results(
        self,
        oil_id: str | None,
        delivery_type_id: str | None,
        delivery_basis_id: str | None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[SpimexTradingResult], int]:
        subquery = select(func.max(SpimexTradingResult.date)).scalar_subquery()

        base = select(SpimexTradingResult).where(SpimexTradingResult.date == subquery)

        if oil_id is not None:
            base = base.where(SpimexTradingResult.oil_id == oil_id)

        if delivery_basis_id is not None:
            base = base.where(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

        if delivery_type_id is not None:
            base = base.where(SpimexTradingResult.delivery_type_id == delivery_type_id)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = base.order_by(SpimexTradingResult.exchange_product_name.asc()).limit(limit).offset(offset)

        raw = await self.session.execute(stmt)
        return list(raw.scalars().all()), total
