from datetime import date

from pydantic import BaseModel, Field


class Filters(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    product: str | None = None
    category: str | None = None
    import_id: int | None = None
    compare: bool = False


class SalesQuery(Filters):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)
    sort_by: str = "fecha"
    sort_order: str = "desc"
