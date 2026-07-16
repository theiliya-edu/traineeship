import datetime

import factory

from shared.database.models import SpimexTradingResult


class SpimexTradingResultFactory(factory.Factory):
    class Meta:
        model = SpimexTradingResult

    id = factory.Sequence(lambda n: n + 1)
    exchange_product_id = factory.Sequence(lambda n: f"A{n % 100:03d}BCC{n % 10}")
    exchange_product_name = factory.Sequence(lambda n: f"Продукт-{n}")
    oil_id = factory.LazyAttribute(lambda o: o.exchange_product_id[:4])
    delivery_basis_id = factory.LazyAttribute(lambda o: o.exchange_product_id[4:7])
    delivery_basis_name = "Базис поставки"
    delivery_type_id = factory.LazyAttribute(lambda o: o.exchange_product_id[-1])
    volume = factory.Sequence(lambda n: (n + 1) * 100)
    total = factory.Sequence(lambda n: (n + 1) * 10000)
    count = factory.Sequence(lambda n: (n + 1) * 10)
    date = factory.LazyFunction(datetime.date.today)
