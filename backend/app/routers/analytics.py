from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories import analytics_repo
from app.routers.deps import CommonFilters
from app.schemas import (
    CategoryPoint,
    DimensionsOut,
    ProductPoint,
    SummaryOut,
    TimeseriesOut,
)
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analitica"])


@router.get("/summary", response_model=SummaryOut)
def summary(
    filters: CommonFilters = Depends(),
    compare: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> SummaryOut:
    return analytics_service.build_summary(db, compare=compare, **filters.as_dict())


@router.get("/timeseries", response_model=TimeseriesOut)
def timeseries(
    filters: CommonFilters = Depends(),
    granularity: str = Query(default="day", pattern="^(day|week|month)$"),
    db: Session = Depends(get_db),
) -> TimeseriesOut:
    return analytics_service.build_timeseries(db, granularity=granularity, **filters.as_dict())


@router.get("/categories", response_model=list[CategoryPoint])
def categories(filters: CommonFilters = Depends(), db: Session = Depends(get_db)) -> list[CategoryPoint]:
    return analytics_service.build_categories(db, **filters.as_dict())


@router.get("/products", response_model=list[ProductPoint])
def products(
    filters: CommonFilters = Depends(),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[ProductPoint]:
    return analytics_service.build_products(db, limit=limit, **filters.as_dict())


@router.get("/dimensions", response_model=DimensionsOut)
def dimensions(db: Session = Depends(get_db)) -> DimensionsOut:
    products_list, categories_list = analytics_repo.distinct_dimensions(db)
    return DimensionsOut(products=products_list, categories=categories_list)
