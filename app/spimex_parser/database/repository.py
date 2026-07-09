from spimex_parser.database.helper import Session
from spimex_parser.database.models import SpimexTradingResult
from spimex_parser.dto import SpimexTradingResultDTO


def save_in_db(data: list[SpimexTradingResultDTO]) -> None:
    with Session() as session:
        for res in data:
            session.add(
                SpimexTradingResult(
                    exchange_product_id=res.exchange_product_id,
                    exchange_product_name=res.exchange_product_name,
                    oil_id=res.oil_id,
                    delivery_basis_id=res.delivery_basis_id,
                    delivery_basis_name=res.delivery_basis_name,
                    delivery_type_id=res.delivery_type_id,
                    volume=res.volume,
                    total=res.total,
                    count=res.count,
                    date=res.date,
                ),
            )

        session.commit()
