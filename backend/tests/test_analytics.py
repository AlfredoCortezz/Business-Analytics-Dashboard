def test_summary_metrics(seeded_client):
    response = seeded_client.get("/api/analytics/summary")
    assert response.status_code == 200
    body = response.json()
    # 2*8.50 + 1*6.00 + 4*8.50 + 3*4.20 = 17 + 6 + 34 + 12.6 = 69.6
    assert body["total_revenue"] == 69.6
    assert body["total_sales"] == 4
    assert body["avg_ticket"] == 17.4
    assert body["top_product"]["name"] == "Café"


def test_summary_filters_by_category(seeded_client):
    body = seeded_client.get("/api/analytics/summary?category=Bebidas").json()
    assert body["total_sales"] == 4
    empty = seeded_client.get("/api/analytics/summary?category=Nada").json()
    assert empty["total_sales"] == 0
    assert empty["total_revenue"] == 0


def test_summary_comparison(seeded_client):
    body = seeded_client.get(
        "/api/analytics/summary?date_from=2024-03-03&date_to=2024-03-04&compare=true"
    ).json()
    assert body["comparison"] is not None
    assert body["comparison"]["previous_period"]["date_from"] == "2024-03-01"
    assert body["comparison"]["previous_period"]["date_to"] == "2024-03-02"


def test_timeseries_daily(seeded_client):
    body = seeded_client.get("/api/analytics/timeseries?granularity=day").json()
    assert body["granularity"] == "day"
    assert len(body["points"]) == 4
    assert body["points"][0]["sales_count"] == 1


def test_timeseries_month(seeded_client):
    body = seeded_client.get("/api/analytics/timeseries?granularity=month").json()
    assert len(body["points"]) == 1
    assert body["points"][0]["period"] == "2024-03"


def test_categories_distribution(seeded_client):
    body = seeded_client.get("/api/analytics/categories").json()
    assert len(body) == 1
    assert body[0]["category"] == "Bebidas"
    assert body[0]["percentage"] == 100.0


def test_products_ranking(seeded_client):
    body = seeded_client.get("/api/analytics/products?limit=2").json()
    assert body[0]["product"] == "Café"
    assert len(body) <= 2


def test_dimensions(seeded_client):
    body = seeded_client.get("/api/analytics/dimensions").json()
    assert set(body["categories"]) == {"Bebidas"}
    assert "Café" in body["products"]


def test_analytics_empty_dataset(client):
    summary = client.get("/api/analytics/summary").json()
    assert summary["total_revenue"] == 0
    assert summary["total_sales"] == 0
    assert summary["top_product"] is None
    assert client.get("/api/analytics/timeseries").json()["points"] == []
    assert client.get("/api/analytics/categories").json() == []
