from tests.fixtures.build_files import (
    csv_bytes,
    csv_missing_columns,
    csv_with_bad_rows,
    xlsx_bytes,
)


def _upload(client, filename, content, content_type="text/csv"):
    return client.post(
        "/api/imports",
        files={"file": (filename, content, content_type)},
    )


def test_upload_valid_csv_creates_pending(client):
    response = _upload(client, "ventas.csv", csv_bytes())
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["total_rows"] == 10
    assert body["accepted_rows"] == 10
    assert body["rejected_rows"] == 0
    assert body["duplicate_rows"] == 0


def test_upload_valid_xlsx(client):
    response = _upload(
        client,
        "ventas.xlsx",
        xlsx_bytes(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    assert response.status_code == 201
    assert response.json()["accepted_rows"] == 10


def test_upload_rejects_unsupported_extension(client):
    response = _upload(client, "datos.txt", b"hola")
    assert response.status_code == 415


def test_upload_rejects_empty_file(client):
    response = _upload(client, "vacio.csv", b"")
    assert response.status_code == 400


def test_upload_rejects_missing_columns(client):
    response = _upload(client, "incompleto.csv", csv_missing_columns())
    assert response.status_code == 400
    assert "columnas requeridas" in response.json()["detail"].lower()


def test_upload_reports_bad_and_duplicate_rows(client):
    response = _upload(client, "sucio.csv", csv_with_bad_rows())
    assert response.status_code == 201
    body = response.json()
    assert body["total_rows"] == 8
    assert body["accepted_rows"] == 2
    assert body["duplicate_rows"] == 1
    assert body["rejected_rows"] == 5
    fields = {error["field"] for error in body["errors"]}
    assert {"fecha", "producto", "cantidad", "precio_unitario"} <= fields


def test_confirm_import_loads_sales(client):
    created = _upload(client, "ventas.csv", csv_bytes()).json()
    confirmed = client.post(f"/api/imports/{created['id']}/confirm")
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"

    sales = client.get("/api/sales").json()
    assert sales["total"] == 10


def test_confirm_twice_conflicts(client):
    created = _upload(client, "ventas.csv", csv_bytes()).json()
    client.post(f"/api/imports/{created['id']}/confirm")
    again = client.post(f"/api/imports/{created['id']}/confirm")
    assert again.status_code == 400


def test_delete_import_removes_sales(client):
    created = _upload(client, "ventas.csv", csv_bytes()).json()
    client.post(f"/api/imports/{created['id']}/confirm")
    deleted = client.delete(f"/api/imports/{created['id']}")
    assert deleted.status_code == 204
    assert client.get("/api/sales").json()["total"] == 0
    assert client.get(f"/api/imports/{created['id']}").status_code == 404


def test_list_imports_paginated(client):
    _upload(client, "ventas.csv", csv_bytes())
    _upload(client, "ventas2.csv", csv_bytes())
    listing = client.get("/api/imports?page=1&page_size=1").json()
    assert listing["total"] == 2
    assert len(listing["items"]) == 1
