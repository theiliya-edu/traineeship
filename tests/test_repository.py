import datetime

from factories import SpimexTradingResultFactory


async def test_last_trading_dates_are_distinct_sorted_and_limited(repo, db_session):
    today = datetime.date.today()
    dates = [today, today, today - datetime.timedelta(days=1), today - datetime.timedelta(days=2)]
    db_session.add_all([SpimexTradingResultFactory.build(date=date) for date in dates])
    await db_session.commit()

    result = await repo.get_last_trading_dates(limit=2)

    assert result == [today, today - datetime.timedelta(days=1)]


async def test_dynamics_applies_product_filters_and_date_range(repo, db_session):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    matching = SpimexTradingResultFactory.build(
        exchange_product_id="A100BCC00",
        oil_id="A100",
        delivery_basis_id="BCC",
        delivery_type_id="0",
        date=today,
    )
    db_session.add_all(
        [
            matching,
            SpimexTradingResultFactory.build(
                exchange_product_id="A200BCC00",
                oil_id="A200",
                delivery_basis_id="BCC",
                delivery_type_id="0",
                date=today,
            ),
            SpimexTradingResultFactory.build(
                exchange_product_id="A100BCC00",
                oil_id="A100",
                delivery_basis_id="BCC",
                delivery_type_id="0",
                date=yesterday,
            ),
        ]
    )
    await db_session.commit()

    result = await repo.get_dynamics(
        oil_id="A100",
        delivery_basis_id="BCC",
        delivery_type_id="0",
        start_date=today,
        end_date=today,
    )

    assert [item.id for item in result] == [matching.id]


async def test_trading_results_use_latest_date_and_apply_filter(repo, db_session):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    expected = SpimexTradingResultFactory.build(date=today, oil_id="A100", exchange_product_id="A100BCC00")
    db_session.add_all(
        [
            expected,
            SpimexTradingResultFactory.build(date=today, oil_id="A200", exchange_product_id="A200BCC00"),
            SpimexTradingResultFactory.build(date=yesterday, oil_id="A100", exchange_product_id="A100BCC00"),
        ]
    )
    await db_session.commit()

    results, total = await repo.get_trading_results(
        oil_id="A100",
        delivery_basis_id=None,
        delivery_type_id=None,
    )

    assert total == 1
    assert [item.id for item in results] == [expected.id]


async def test_trading_results_apply_pagination(repo, db_session):
    today = datetime.date.today()
    db_session.add_all([SpimexTradingResultFactory.build(date=today) for _ in range(5)])
    await db_session.commit()

    first_page, total = await repo.get_trading_results(
        oil_id=None,
        delivery_basis_id=None,
        delivery_type_id=None,
        limit=2,
        offset=0,
    )
    second_page, _ = await repo.get_trading_results(
        oil_id=None,
        delivery_basis_id=None,
        delivery_type_id=None,
        limit=2,
        offset=2,
    )

    assert total == 5
    assert len(first_page) == len(second_page) == 2
    assert {item.id for item in first_page}.isdisjoint(item.id for item in second_page)
