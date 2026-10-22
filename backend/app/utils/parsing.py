import math
import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import pandas as pd

HEADER_ALIASES: dict[str, str] = {
    "fecha": "fecha",
    "date": "fecha",
    "fecha_venta": "fecha",
    "dia": "fecha",
    "producto": "producto",
    "product": "producto",
    "nombre_producto": "producto",
    "item": "producto",
    "articulo": "producto",
    "categoria": "categoria",
    "category": "categoria",
    "rubro": "categoria",
    "cantidad": "cantidad",
    "quantity": "cantidad",
    "qty": "cantidad",
    "unidades": "cantidad",
    "precio_unitario": "precio_unitario",
    "precio_unit": "precio_unitario",
    "unit_price": "precio_unitario",
    "precio": "precio_unitario",
    "price": "precio_unitario",
    "precio_venta": "precio_unitario",
    "ventas_totales": "ventas_totales",
    "total": "ventas_totales",
    "total_sales": "ventas_totales",
    "monto": "ventas_totales",
    "importe": "ventas_totales",
    "venta_total": "ventas_totales",
}

REQUIRED_COLUMNS = ("fecha", "producto", "categoria", "cantidad", "precio_unitario")
OPTIONAL_COLUMNS = ("ventas_totales",)


def normalize_header(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).strip().lower()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", "_", text).strip("_")


def map_columns(columns: list[object]) -> dict[str, object]:
    mapping: dict[str, object] = {}
    for column in columns:
        canonical = HEADER_ALIASES.get(normalize_header(column))
        if canonical and canonical not in mapping:
            mapping[canonical] = column
    return mapping


def is_empty(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def parse_date(value: object) -> date | None:
    if is_empty(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        parsed = pd.to_datetime(str(value).strip(), dayfirst=True, errors="coerce")
    except (ValueError, TypeError):
        return None
    if pd.isna(parsed):
        return None
    return parsed.date()


def parse_decimal(value: object) -> Decimal | None:
    if is_empty(value):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    text = str(value).strip()
    negative = text.startswith("-") or (text.startswith("(") and text.endswith(")"))
    text = re.sub(r"[^0-9.,]", "", text)
    if not text:
        return None
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        result = Decimal(text)
    except InvalidOperation:
        return None
    return -result if negative else result


def parse_quantity(value: object) -> int | None:
    decimal_value = parse_decimal(value)
    if decimal_value is None:
        return None
    if decimal_value != decimal_value.to_integral_value():
        return None
    quantity = int(decimal_value)
    return quantity if quantity > 0 else None
