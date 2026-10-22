def test_report_csv_content(seeded_client):
    response = seeded_client.get("/api/reports/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]
    text = response.content.decode("utf-8-sig")
    lines = [line for line in text.strip().splitlines() if line]
    assert lines[0].startswith("id,fecha,producto")
    assert len(lines) == 5


def test_report_csv_respects_filters(seeded_client):
    response = seeded_client.get("/api/reports/csv?product=Café")
    text = response.content.decode("utf-8-sig")
    rows = [line for line in text.replace("\r\n", "\n").strip().splitlines() if line]
    assert len(rows) == 3


def test_report_pdf_is_valid(seeded_client):
    response = seeded_client.get("/api/reports/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 1000


def test_report_pdf_empty_dataset(client):
    response = client.get("/api/reports/pdf")
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
