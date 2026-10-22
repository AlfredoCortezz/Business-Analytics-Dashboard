from datetime import date

from fastapi import Query


class CommonFilters:
    def __init__(
        self,
        date_from: date | None = Query(default=None, alias="date_from"),
        date_to: date | None = Query(default=None, alias="date_to"),
        product: str | None = Query(default=None),
        category: str | None = Query(default=None),
        import_id: int | None = Query(default=None),
    ):
        self.date_from = date_from
        self.date_to = date_to
        self.product = product
        self.category = category
        self.import_id = import_id

    def as_dict(self) -> dict:
        return {
            "date_from": self.date_from,
            "date_to": self.date_to,
            "product": self.product or None,
            "category": self.category or None,
            "import_id": self.import_id,
        }
