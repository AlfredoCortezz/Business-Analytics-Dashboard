import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.core.database import Base, get_db  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
from app.models import Import, Sale  # noqa: E402


@pytest.fixture()
def db_session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session, tmp_path, monkeypatch):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr("app.core.config.settings.upload_dir", str(upload_dir), raising=False)
    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def seeded_client(client, db_session):
    record = Import(
        filename="semilla.csv",
        status="confirmed",
        total_rows=4,
        accepted_rows=4,
        checksum="seed",
    )
    db_session.add(record)
    db_session.flush()

    from datetime import date
    from decimal import Decimal

    rows = [
        (date(2024, 3, 1), "Café", "Bebidas", 2, "8.50"),
        (date(2024, 3, 2), "Té", "Bebidas", 1, "6.00"),
        (date(2024, 3, 3), "Café", "Bebidas", 4, "8.50"),
        (date(2024, 3, 4), "Jugo", "Bebidas", 3, "4.20"),
    ]
    for fecha, producto, categoria, cantidad, precio in rows:
        price = Decimal(precio)
        db_session.add(
            Sale(
                import_id=record.id,
                fecha=fecha,
                producto=producto,
                categoria=categoria,
                cantidad=cantidad,
                precio_unitario=price,
                total=(Decimal(cantidad) * price),
            )
        )
    db_session.commit()
    return client
