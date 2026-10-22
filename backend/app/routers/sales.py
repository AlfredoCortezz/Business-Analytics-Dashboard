from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.repositories import sales_repo
from app.routers.deps import CommonFilters
from app.schemas import Paginated, SaleOut

router = APIRouter(prefix="/sales", tags=["ventas"])


def _to_sale_out(sale) -> SaleOut:
    return SaleOut(
        id=sale.id,
        import_id=sale.import_id,
        fecha=sale.fecha,
        producto=sale.producto,
        categoria=sale.categoria,
        cantidad=sale.cantidad,
        precio_unitario=sale.precio_unitario,
        total=sale.total,
        row_warnings=sale.row_warnings or [],
    )


@router.get("", response_model=Paginated[SaleOut])
def list_sales(
    filters: CommonFilters = Depends(),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    sort_by: str = Query(default="fecha"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
) -> Paginated[SaleOut]:
    items, total = sales_repo.list_paginated(
        db,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        **filters.as_dict(),
    )
    return Paginated[SaleOut](
        items=[_to_sale_out(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)) -> SaleOut:
    sale = sales_repo.get(db, sale_id)
    if sale is None:
        raise NotFoundError("Venta no encontrada.")
    return _to_sale_out(sale)
