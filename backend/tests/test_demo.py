def test_seed_demo_creates_data(client):
    response = client.post("/api/demo/seed")
    assert response.status_code == 200
    body = response.json()
    assert body["created"] is True
    assert body["sales"] > 0

    summary = client.get("/api/analytics/summary").json()
    assert summary["total_sales"] == body["sales"]


def test_seed_demo_is_idempotent(client):
    first = client.post("/api/demo/seed").json()
    second = client.post("/api/demo/seed").json()
    assert second["created"] is False

    imports = client.get("/api/imports").json()
    demo_imports = [item for item in imports["items"] if item["is_demo"]]
    assert len(demo_imports) == 1
    assert first["sales"] == demo_imports[0]["accepted_rows"]


def test_demo_data_is_flagged(client):
    client.post("/api/demo/seed")
    imports = client.get("/api/imports").json()["items"]
    assert any(item["is_demo"] and item["filename"].startswith("DEMO") for item in imports)


def test_reset_demo_removes_data(client):
    client.post("/api/demo/seed")
    client.delete("/api/demo/seed")
    assert client.get("/api/analytics/summary").json()["total_sales"] == 0
    assert client.get("/api/imports").json()["total"] == 0
