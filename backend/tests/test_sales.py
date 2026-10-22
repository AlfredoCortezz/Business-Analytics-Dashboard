def test_list_sales_with_filters(seeded_client):
    response = seeded_client.get("/api/sales?product=Café")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert all(item["producto"] == "Café" for item in body["items"])


def test_list_sales_date_filter(seeded_client):
    response = seeded_client.get("/api/sales?date_from=2024-03-02&date_to=2024-03-03")
    assert response.json()["total"] == 2


def test_list_sales_sorting(seeded_client):
    response = seeded_client.get("/api/sales?sort_by=cantidad&sort_order=asc")
    quantities = [item["cantidad"] for item in response.json()["items"]]
    assert quantities == sorted(quantities)


def test_sales_pagination(seeded_client):
    page = seeded_client.get("/api/sales?page=2&page_size=2").json()
    assert page["page"] == 2
    assert len(page["items"]) == 2
    assert page["total"] == 4


def test_get_sale_detail(seeded_client):
    sale_id = seeded_client.get("/api/sales").json()["items"][0]["id"]
    response = seeded_client.get(f"/api/sales/{sale_id}")
    assert response.status_code == 200
    assert response.json()["id"] == sale_id


def test_get_missing_sale_returns_404(seeded_client):
    assert seeded_client.get("/api/sales/9999").status_code == 404


def test_empty_results(seeded_client):
    response = seeded_client.get("/api/sales?category=Inexistente")
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []
