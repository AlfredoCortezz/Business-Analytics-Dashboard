from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Sale


def apply_filters(
    statement: Select,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    product: str | None = None,
    category: str | None = None,
    import_id: int | None = None,
) -> Select:
    if date_from is not None:
        statement = statement.where(Sale.fecha >= date_from)
    if date_to is not None:
        statement = statement.where(Sale.fecha <= date_to)
    if product:
        statement = statement.where(Sale.producto == product)
    if category:
        statement = statement.where(Sale.categoria == category)
    if import_id is not None:
        statement = statement.where(Sale.import_id == import_id)
    return statement


def list_paginated(
    db: Session,
    *,
    page: int,
    page_size: int,
    sort_by: str = "fecha",
    sort_order: str = "desc",
    **filters,
) -> tuple[list[Sale], int]:
    sort_column = {
        "fecha": Sale.fecha,
        "producto": Sale.producto,
        "categoria": Sale.categoria,
        "cantidad": Sale.cantidad,
        "precio_unitario": Sale.precio_unitario,
        "total": Sale.total,
        "id": Sale.id,
    }.get(sort_by, Sale.fecha)
    order = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    base = apply_filters(select(Sale), **filters)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    statement = base.order_by(order, Sale.id.desc()).offset((page - 1) * page_size).limit(page_size)
    return list(db.scalars(statement)), total


def get(db: Session, sale_id: int) -> Sale | None:
    return db.get(Sale, sale_id)


def list_filtered(db: Session, **filters) -> list[Sale]:
    statement = apply_filters(select(Sale), **filters).order_by(Sale.fecha.asc(), Sale.id.asc())
    return list(db.scalars(statement))
