from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Sale
from app.repositories.sales_repo import apply_filters


def totals(db: Session, **filters) -> tuple[float, int]:
    statement = apply_filters(
        select(func.coalesce(func.sum(Sale.total), 0), func.count(Sale.id)), **filters
    )
    revenue, count = db.execute(statement).one()
    return float(revenue or 0), int(count or 0)


def top_product(db: Session, **filters) -> tuple[str, float, int] | None:
    statement = apply_filters(
        select(Sale.producto, func.sum(Sale.total), func.sum(Sale.cantidad)), **filters
    )
    statement = statement.group_by(Sale.producto).order_by(func.sum(Sale.total).desc()).limit(1)
    row = db.execute(statement).first()
    if row is None:
        return None
    return row[0], float(row[1] or 0), int(row[2] or 0)


def daily_totals(db: Session, **filters) -> list[tuple[date, float, int]]:
    statement = apply_filters(
        select(Sale.fecha, func.sum(Sale.total), func.count(Sale.id)), **filters
    )
    statement = statement.group_by(Sale.fecha).order_by(Sale.fecha.asc())
    return [(row[0], float(row[1] or 0), int(row[2] or 0)) for row in db.execute(statement)]


def by_category(db: Session, **filters) -> list[tuple[str, float, int]]:
    statement = apply_filters(
        select(Sale.categoria, func.sum(Sale.total), func.count(Sale.id)), **filters
    )
    statement = statement.group_by(Sale.categoria).order_by(func.sum(Sale.total).desc())
    return [(row[0], float(row[1] or 0), int(row[2] or 0)) for row in db.execute(statement)]


def by_product(db: Session, limit: int, **filters) -> list[tuple[str, float, int, int]]:
    statement = apply_filters(
        select(Sale.producto, func.sum(Sale.total), func.sum(Sale.cantidad), func.count(Sale.id)),
        **filters,
    )
    statement = (
        statement.group_by(Sale.producto)
        .order_by(func.sum(Sale.total).desc())
        .limit(limit)
    )
    return [
        (row[0], float(row[1] or 0), int(row[2] or 0), int(row[3] or 0))
        for row in db.execute(statement)
    ]


def date_range(db: Session) -> tuple[date | None, date | None]:
    row = db.execute(select(func.min(Sale.fecha), func.max(Sale.fecha))).one()
    return row[0], row[1]


def distinct_dimensions(db: Session) -> tuple[list[str], list[str]]:
    products = list(db.scalars(select(Sale.producto).distinct().order_by(Sale.producto).limit(500)))
    categories = list(
        db.scalars(select(Sale.categoria).distinct().order_by(Sale.categoria).limit(500))
    )
    return products, categories
