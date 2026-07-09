import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class PaginationParams(BaseModel):
    limit: int
    offset: int


class TradingResultFilters(BaseModel):
    oil_id: str | None = None
    delivery_basis_id: str | None = None
    delivery_type_id: str | None = None


class DynamicsFilters(BaseModel):
    oil_id: Annotated[str, Field(description="Код нефти или нефтепродукта")]
    delivery_basis_id: Annotated[str, Field(description="Код базиса поставки")]
    delivery_type_id: Annotated[str, Field(description="Код типа поставки")]
    start_date: Annotated[
        datetime.date,
        Field(
            default_factory=lambda: datetime.date.today() - datetime.timedelta(days=30),
            description="Начальная дата периода",
        ),
    ]
    end_date: Annotated[
        datetime.date,
        Field(default_factory=datetime.date.today, description="Конечная дата периода"),
    ]


class TradingResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[int, Field(description="Уникальный идентификатор записи")]
    exchange_product_id: Annotated[str, Field(description="Код инструмента")]
    exchange_product_name: Annotated[str, Field(description="Наименование инструмента")]
    oil_id: Annotated[str, Field(description="Код нефти или нефтепродукта")]
    delivery_basis_id: Annotated[str, Field(description="Код базиса поставки")]
    delivery_basis_name: Annotated[str, Field(description="Наименование базиса поставки")]
    delivery_type_id: Annotated[str, Field(description="Код типа поставки")]
    volume: Annotated[int | None, Field(default=None, description="Объем договоров в тоннах")]
    total: Annotated[int | None, Field(default=None, description="Объем договоров")]
    count: Annotated[int | None, Field(default=None, description="Количество договоров")]
    date: Annotated[datetime.date, Field(description="Дата торгов")]


class PaginatedTradingResults(BaseModel):
    items: Annotated[list[TradingResultResponse], Field(description="Список результатов торгов")]
    total: Annotated[int, Field(description="Общее количество записей")]
    page: Annotated[int, Field(description="Номер текущей страницы")]
    limit: Annotated[int, Field(description="Количество элементов на странице")]


class TradingDateResponse(BaseModel):
    date: Annotated[datetime.date, Field(description="Дата торгов")]
