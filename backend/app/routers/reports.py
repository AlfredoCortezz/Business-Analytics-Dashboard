from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories import sales_repo
from app.routers.deps import CommonFilters
from app.services import analytics_service, report_service

router = APIRouter(prefix="/reports", tags=["reportes"])

CSV_MEDIA = "text/csv"


def _filename(extension: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"reporte-ventas-{stamp}.{extension}"


@router.get("/csv")
def report_csv(filters: CommonFilters = Depends(), db: Session = Depends(get_db)) -> Response:
    sales = sales_repo.list_filtered(db, **filters.as_dict())
    content = report_service.build_csv(sales)
    return Response(
        content=content.encode("utf-8-sig"),
        media_type=f"{CSV_MEDIA}; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{_filename("csv")}"'},
    )


@router.get("/pdf")
def report_pdf(
    filters: CommonFilters = Depends(),
    compare: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    active = filters.as_dict()
    summary = analytics_service.build_summary(db, compare=compare, **active)
    period = {"date_from": active.get("date_from"), "date_to": active.get("date_to")}
    pdf_bytes = report_service.build_pdf(db, filters=active, period=period, summary=summary)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_filename("pdf")}"'},
    )
