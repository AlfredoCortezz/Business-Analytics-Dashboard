from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.repositories import analytics_repo
from app.schemas import (
    CategoryPoint,
    ComparisonOut,
    Period,
    ProductPoint,
    SummaryOut,
    TimeseriesOut,
    TimeseriesPoint,
    TopProduct,
)


def _filters(
    date_from: date | None,
    date_to: date | None,
    product: str | None,
    category: str | None,
    import_id: int | None,
) -> dict:
    return {
        "date_from": date_from,
        "date_to": date_to,
        "product": product or None,
        "category": category or None,
        "import_id": import_id,
    }


def _pct_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 2)


def _previous_period(date_from: date | None, date_to: date | None, db: Session) -> tuple[date, date] | None:
    if date_from is None or date_to is None:
        overall_from, overall_to = analytics_repo.date_range(db)
        if overall_from is None or overall_to is None:
            return None
        date_from, date_to = overall_from, overall_to
    span = (date_to - date_from).days + 1
    if span < 1:
        return None
    previous_to = date_from - timedelta(days=1)
    previous_from = previous_to - timedelta(days=span - 1)
    return previous_from, previous_to


def build_summary(
    db: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    product: str | None = None,
    category: str | None = None,
    import_id: int | None = None,
    compare: bool = False,
) -> SummaryOut:
    filters = _filters(date_from, date_to, product, category, import_id)
    revenue, sales_count = analytics_repo.totals(db, **filters)
    avg_ticket = round(revenue / sales_count, 2) if sales_count else 0.0
    top = analytics_repo.top_product(db, **filters)
    top_product = TopProduct(name=top[0], revenue=top[1], quantity=top[2]) if top else None

    comparison = None
    if compare:
        previous = _previous_period(date_from, date_to, db)
        if previous is not None:
            prev_from, prev_to = previous
            prev_filters = _filters(prev_from, prev_to, product, category, import_id)
            prev_revenue, prev_sales = analytics_repo.totals(db, **prev_filters)
            prev_avg = round(prev_revenue / prev_sales, 2) if prev_sales else 0.0
            comparison = ComparisonOut(
                previous_revenue=prev_revenue,
                previous_sales=prev_sales,
                previous_avg_ticket=prev_avg,
                revenue_change_pct=_pct_change(revenue, prev_revenue),
                sales_change_pct=_pct_change(float(sales_count), float(prev_sales)),
                avg_ticket_change_pct=_pct_change(avg_ticket, prev_avg),
                previous_period=Period(date_from=prev_from, date_to=prev_to),
            )

    return SummaryOut(
        total_revenue=round(revenue, 2),
        total_sales=sales_count,
        avg_ticket=avg_ticket,
        top_product=top_product,
        period=Period(date_from=date_from, date_to=date_to),
        comparison=comparison,
    )


def _bucket(day: date, granularity: str) -> str:
    if granularity == "month":
        return day.strftime("%Y-%m")
    if granularity == "week":
        iso_year, iso_week, _ = day.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    return day.isoformat()


def build_timeseries(
    db: Session,
    *,
    granularity: str = "day",
    date_from: date | None = None,
    date_to: date | None = None,
    product: str | None = None,
    category: str | None = None,
    import_id: int | None = None,
) -> TimeseriesOut:
    if granularity not in {"day", "week", "month"}:
        granularity = "day"
    filters = _filters(date_from, date_to, product, category, import_id)
    rows = analytics_repo.daily_totals(db, **filters)

    buckets: dict[str, list[float]] = {}
    for day, revenue, count in rows:
        key = _bucket(day, granularity)
        entry = buckets.setdefault(key, [0.0, 0.0])
        entry[0] += revenue
        entry[1] += count

    points = [
        TimeseriesPoint(period=key, revenue=round(value[0], 2), sales_count=int(value[1]))
        for key, value in sorted(buckets.items())
    ]
    return TimeseriesOut(granularity=granularity, points=points)


def build_categories(db: Session, **filters) -> list[CategoryPoint]:
    rows = analytics_repo.by_category(db, **filters)
    total = sum(row[1] for row in rows) or 0.0
    return [
        CategoryPoint(
            category=row[0],
            revenue=round(row[1], 2),
            sales_count=row[2],
            percentage=round(row[1] / total * 100, 2) if total else 0.0,
        )
        for row in rows
    ]


def build_products(db: Session, limit: int = 10, **filters) -> list[ProductPoint]:
    rows = analytics_repo.by_product(db, limit=limit, **filters)
    return [
        ProductPoint(product=row[0], revenue=round(row[1], 2), quantity=row[2], sales_count=row[3])
        for row in rows
    ]
