from datetime import date, datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.filters import Filters, SalesQuery

T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ImportErrorItem(BaseModel):
    row: int
    field: str | None = None
    message: str


class ImportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    duplicate_rows: int
    is_demo: bool
    created_at: datetime
    confirmed_at: datetime | None = None


class ImportDetail(ImportOut):
    errors: list[ImportErrorItem] = Field(default_factory=list)


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    import_id: int
    fecha: date
    producto: str
    categoria: str
    cantidad: int
    precio_unitario: Decimal
    total: Decimal
    row_warnings: list[str] = Field(default_factory=list)


class Period(BaseModel):
    date_from: date | None = None
    date_to: date | None = None


class TopProduct(BaseModel):
    name: str
    revenue: float
    quantity: int


class ComparisonOut(BaseModel):
    previous_revenue: float
    previous_sales: int
    previous_avg_ticket: float
    revenue_change_pct: float | None = None
    sales_change_pct: float | None = None
    avg_ticket_change_pct: float | None = None
    previous_period: Period


class SummaryOut(BaseModel):
    total_revenue: float
    total_sales: int
    avg_ticket: float
    top_product: TopProduct | None = None
    period: Period
    comparison: ComparisonOut | None = None


class TimeseriesPoint(BaseModel):
    period: str
    revenue: float
    sales_count: int


class TimeseriesOut(BaseModel):
    granularity: str
    points: list[TimeseriesPoint]


class CategoryPoint(BaseModel):
    category: str
    revenue: float
    sales_count: int
    percentage: float


class ProductPoint(BaseModel):
    product: str
    revenue: float
    quantity: int
    sales_count: int


class DimensionsOut(BaseModel):
    products: list[str]
    categories: list[str]


class DemoOut(BaseModel):
    created: bool
    imports: int
    sales: int
    message: str


__all__ = [
    "Paginated",
    "ImportErrorItem",
    "ImportOut",
    "ImportDetail",
    "SaleOut",
    "Period",
    "TopProduct",
    "ComparisonOut",
    "SummaryOut",
    "TimeseriesPoint",
    "TimeseriesOut",
    "CategoryPoint",
    "ProductPoint",
    "DimensionsOut",
    "DemoOut",
    "Filters",
    "SalesQuery",
]
