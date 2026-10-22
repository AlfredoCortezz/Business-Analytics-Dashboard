from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Import


def create(db: Session, **values) -> Import:
    record = Import(**values)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get(db: Session, import_id: int) -> Import | None:
    return db.get(Import, import_id)


def list_paginated(db: Session, page: int, page_size: int) -> tuple[list[Import], int]:
    total = db.scalar(select(func.count(Import.id))) or 0
    statement = (
        select(Import)
        .order_by(Import.created_at.desc(), Import.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(db.scalars(statement)), total


def save(db: Session, record: Import) -> Import:
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def delete(db: Session, record: Import) -> None:
    db.delete(record)
    db.commit()
