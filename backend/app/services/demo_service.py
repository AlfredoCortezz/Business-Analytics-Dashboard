import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import Import, Sale
from app.models.imports import utc_now

DEMO_FILENAME = "DEMO-datos-ficticios.csv"
CATALOG: dict[str, list[tuple[str, float]]] = {
    "Bebidas": [("Café molido", 8.5), ("Té verde", 6.0), ("Jugo natural", 4.2), ("Agua mineral", 1.8)],
    "Panadería": [("Pan integral", 3.5), ("Croissant", 2.2), ("Muffin", 2.8), ("Torta de chocolate", 12.0)],
    "Snacks": [("Barra de cereal", 2.5), ("Frutos secos", 5.5), ("Galletas", 3.0)],
    "Tecnología": [("Teclado", 45.0), ("Mouse", 25.0), ("Auriculares", 60.0), ("Monitor", 180.0)],
    "Papelería": [("Cuaderno", 4.0), ("Bolígrafo", 1.2), ("Resma A4", 7.5)],
}


def _demo_exists(db: Session) -> bool:
    return db.scalar(select(func.count(Import.id)).where(Import.is_demo.is_(True))) or 0


def seed_demo(db: Session, months: int = 12) -> int:
    if _demo_exists(db):
        return 0

    rng = random.Random(20240101)
    today = date.today()
    start = today - timedelta(days=30 * months)

    record = Import(
        filename=DEMO_FILENAME,
        status="confirmed",
        is_demo=True,
        checksum="demo-dataset",
        confirmed_at=utc_now(),
        created_at=utc_now(),
    )
    db.add(record)
    db.flush()

    created = 0
    current = start
    while current <= today:
        daily_sales = rng.randint(3, 12)
        for _ in range(daily_sales):
            category = rng.choice(list(CATALOG.keys()))
            product, base_price = rng.choice(CATALOG[category])
            quantity = rng.randint(1, 15)
            price = Decimal(str(round(base_price * rng.uniform(0.9, 1.15), 2)))
            total = (Decimal(quantity) * price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            db.add(
                Sale(
                    import_id=record.id,
                    fecha=current,
                    producto=product,
                    categoria=category,
                    cantidad=quantity,
                    precio_unitario=price,
                    total=total,
                )
            )
            created += 1
        current += timedelta(days=1)

    record.total_rows = created
    record.accepted_rows = created
    db.commit()
    return created


def reset_demo(db: Session) -> int:
    ids = list(db.scalars(select(Import.id).where(Import.is_demo.is_(True))))
    if not ids:
        return 0
    db.execute(delete(Sale).where(Sale.import_id.in_(ids)))
    db.execute(delete(Import).where(Import.id.in_(ids)))
    db.commit()
    return len(ids)
