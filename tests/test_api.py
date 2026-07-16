import datetime

import pytest
from factories import SpimexTradingResultFactory


async def test_get_last_trading_dates_returns_dates(client, db_session):
    today = datetime.date.today()
    db_session.add_all(
        [
            SpimexTradingResultFactory.build(date=today),
            SpimexTradingResultFactory.build(date=today - datetime.timedelta(days=1)),
        ]
    )
    await db_session.commit()

    response = await client.get("/v1/trading-results/dates?limit=5")

    assert response.status_code == 200
    assert response.json() == [
        {"date": today.isoformat()},
        {"date": (today - datetime.timedelta(days=1)).isoformat()},
    ]


async def test_get_last_trading_dates_requires_limit(client):
    response = await client.get("/v1/trading-results/dates")

    assert response.status_code == 422


async def test_get_dynamics_returns_filtered_results(client, db_session):
    today = datetime.date.today()
    db_session.add_all(
        [
            SpimexTradingResultFactory.build(
                exchange_product_id="A100BCC00",
                oil_id="A100",
                delivery_basis_id="BCC",
                delivery_type_id="0",
                date=today,
            ),
            SpimexTradingResultFactory.build(
                exchange_product_id="A100BCC01",
                oil_id="A100",
                delivery_basis_id="BCC",
                delivery_type_id="1",
                date=today,
            ),
        ]
    )
    await db_session.commit()

    response = await client.get(
        "/v1/trading-results/dynamics",
        params={
            "oil_id": "A100",
            "delivery_basis_id": "BCC",
            "delivery_type_id": "0",
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["delivery_type_id"] == "0"


@pytest.mark.parametrize("date_field", ["start_date", "end_date"])
async def test_get_dynamics_rejects_invalid_date(client, date_field):
    params = {
        "oil_id": "A100",
        "delivery_basis_id": "BCC",
        "delivery_type_id": "0",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
    }
    params[date_field] = "not-a-date"

    response = await client.get("/v1/trading-results/dynamics", params=params)

    assert response.status_code == 422


async def test_get_trading_results_applies_filter_and_pagination(client, db_session):
    today = datetime.date.today()
    db_session.add_all(
        [
            SpimexTradingResultFactory.build(date=today, oil_id="A100", exchange_product_id=f"A100BCC0{i}")
            for i in range(3)
        ]
        + [SpimexTradingResultFactory.build(date=today, oil_id="A200", exchange_product_id="A200BCC00")]
    )
    await db_session.commit()

    response = await client.get(
        "/v1/trading-results",
        params={"oil_id": "A100", "limit": 2, "offset": 0},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert len(data["items"]) == 2
    assert all(item["oil_id"] == "A100" for item in data["items"])


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
async def test_get_trading_results_rejects_invalid_pagination(client, params):
    response = await client.get("/v1/trading-results", params=params)

    assert response.status_code == 422
