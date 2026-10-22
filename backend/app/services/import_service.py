import hashlib
import io
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError, PayloadTooLargeError, UnsupportedMediaError
from app.models import Import, Sale
from app.repositories import imports_repo
from app.utils.parsing import (
    REQUIRED_COLUMNS,
    is_empty,
    map_columns,
    parse_date,
    parse_decimal,
    parse_quantity,
)

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
MAX_STORED_ERRORS = 500
TOTAL_TOLERANCE = Decimal("0.01")


@dataclass
class ParsedRow:
    row_number: int
    fecha: date
    producto: str
    categoria: str
    cantidad: int
    precio_unitario: Decimal
    total: Decimal
    warnings: list[str] = field(default_factory=list)


@dataclass
class ParseResult:
    accepted: list[ParsedRow]
    total_rows: int
    rejected_rows: int
    duplicate_rows: int
    errors: list[dict]


def _validate_upload(filename: str, content: bytes) -> str:
    if not filename:
        raise UnsupportedMediaError("Debes adjuntar un archivo CSV o Excel.")
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise UnsupportedMediaError(
            "Extensión no admitida. Solo se aceptan archivos .csv y .xlsx."
        )
    if len(content) == 0:
        raise AppError("El archivo está vacío.")
    if len(content) > settings.max_upload_bytes:
        raise PayloadTooLargeError(
            f"El archivo supera el límite de {settings.max_upload_mb} MB."
        )
    return extension


def _read_dataframe(extension: str, content: bytes) -> pd.DataFrame:
    buffer = io.BytesIO(content)
    try:
        if extension == ".csv":
            if content.startswith(b"PK") or content.startswith(b"\xd0\xcf\x11\xe0"):
                raise AppError("El contenido del archivo no corresponde a un CSV válido.")
            try:
                return pd.read_csv(buffer, dtype=object, keep_default_na=False)
            except UnicodeDecodeError:
                buffer.seek(0)
                return pd.read_csv(buffer, dtype=object, encoding="latin-1", keep_default_na=False)
        return pd.read_excel(buffer, dtype=object, engine="openpyxl")
    except AppError:
        raise
    except Exception as exc:  # noqa: BLE001 - se traduce a error de dominio
        raise AppError("No se pudo leer el archivo. Verifica que no esté dañado.") from exc


def parse_content(filename: str, content: bytes) -> tuple[ParseResult, dict, str]:
    extension = _validate_upload(filename, content)
    checksum = hashlib.sha256(content).hexdigest()
    dataframe = _read_dataframe(extension, content)

    if dataframe.empty:
        raise AppError("El archivo no contiene filas de datos.")

    column_map = map_columns(list(dataframe.columns))
    missing = [column for column in REQUIRED_COLUMNS if column not in column_map]
    if missing:
        raise AppError(
            "Faltan columnas requeridas: " + ", ".join(missing) + ". "
            "Se esperan: fecha, producto, categoría, cantidad, precio unitario."
        )

    accepted: list[ParsedRow] = []
    errors: list[dict] = []
    seen_keys: set[tuple] = set()
    duplicate_rows = 0
    total_rows = 0

    for position, (_, raw_row) in enumerate(dataframe.iterrows(), start=2):
        total_rows += 1
        row_errors: list[dict] = []

        def value(column: str):
            column_name = column_map.get(column)
            if column_name is None:
                return None
            return raw_row.get(column_name)

        fecha = parse_date(value("fecha"))
        if fecha is None:
            row_errors.append({"row": position, "field": "fecha", "message": "Fecha inválida o vacía."})

        producto = str(value("producto")).strip() if not is_empty(value("producto")) else ""
        if not producto:
            row_errors.append({"row": position, "field": "producto", "message": "Producto vacío."})

        categoria = str(value("categoria")).strip() if not is_empty(value("categoria")) else ""
        if not categoria:
            row_errors.append({"row": position, "field": "categoria", "message": "Categoría vacía."})

        cantidad = parse_quantity(value("cantidad"))
        if cantidad is None:
            row_errors.append(
                {"row": position, "field": "cantidad", "message": "Cantidad inválida (debe ser un entero mayor que 0)."}
            )

        precio_unitario = parse_decimal(value("precio_unitario"))
        if precio_unitario is None or precio_unitario < 0:
            row_errors.append(
                {"row": position, "field": "precio_unitario", "message": "Precio unitario inválido (debe ser numérico y no negativo)."}
            )

        if row_errors:
            errors.extend(row_errors)
            continue

        total = (Decimal(cantidad) * precio_unitario).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        warnings: list[str] = []

        provided_total = parse_decimal(value("ventas_totales")) if "ventas_totales" in column_map else None
        if provided_total is not None and abs(provided_total - total) > TOTAL_TOLERANCE:
            warnings.append(
                "El total informado ({0}) no coincide con cantidad x precio ({1}). Se usó el valor calculado.".format(
                    provided_total, total
                )
            )

        key = (fecha, producto, categoria, cantidad, precio_unitario)
        if key in seen_keys:
            duplicate_rows += 1
            errors.append(
                {"row": position, "field": None, "message": "Registro duplicado dentro del archivo (omitido)."}
            )
            continue

        seen_keys.add(key)
        accepted.append(
            ParsedRow(
                row_number=position,
                fecha=fecha,
                producto=producto,
                categoria=categoria,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                total=total,
                warnings=warnings,
            )
        )

    result = ParseResult(
        accepted=accepted,
        total_rows=total_rows,
        rejected_rows=len([error for error in errors if error["field"] is not None]),
        duplicate_rows=duplicate_rows,
        errors=errors[:MAX_STORED_ERRORS],
    )
    stats = {
        "total_rows": result.total_rows,
        "accepted_rows": len(accepted),
        "rejected_rows": result.rejected_rows,
        "duplicate_rows": result.duplicate_rows,
        "errors": result.errors,
    }
    return result, stats, checksum


def _serialize_rows(rows: list[ParsedRow]) -> list[dict]:
    return [
        {
            "fecha": row.fecha.isoformat(),
            "producto": row.producto,
            "categoria": row.categoria,
            "cantidad": row.cantidad,
            "precio_unitario": str(row.precio_unitario),
            "total": str(row.total),
            "warnings": row.warnings,
        }
        for row in rows
    ]


def create_pending_import(db: Session, filename: str, content: bytes) -> Import:
    result, stats, checksum = parse_content(filename, content)
    return imports_repo.create(
        db,
        filename=Path(filename).name,
        status="pending",
        total_rows=stats["total_rows"],
        accepted_rows=stats["accepted_rows"],
        rejected_rows=stats["rejected_rows"],
        duplicate_rows=stats["duplicate_rows"],
        errors_json=stats["errors"],
        accepted_rows_json=_serialize_rows(result.accepted),
        checksum=checksum,
        is_demo=False,
    )


def confirm_import(db: Session, import_id: int) -> Import:
    record = imports_repo.get(db, import_id)
    if record is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Importación no encontrada.")
    if record.status == "confirmed":
        raise AppError("La importación ya fue confirmada.")
    if record.status != "pending":
        raise AppError("Solo se pueden confirmar importaciones pendientes.")

    rows: list[dict] | None = record.accepted_rows_json
    if not rows:
        content = _read_stored(record)
        if content is None:
            raise AppError("No hay datos para confirmar esta importación. Vuelve a subir el archivo.")
        result, _, _ = parse_content(record.filename, content)
        rows = _serialize_rows(result.accepted)

    for row in rows:
        db.add(
            Sale(
                import_id=record.id,
                fecha=date.fromisoformat(row["fecha"]),
                producto=row["producto"],
                categoria=row["categoria"],
                cantidad=row["cantidad"],
                precio_unitario=Decimal(row["precio_unitario"]),
                total=Decimal(row["total"]),
                row_warnings=row.get("warnings") or None,
            )
        )
    from app.models.imports import utc_now

    record.status = "confirmed"
    record.confirmed_at = utc_now()
    record.accepted_rows = len(rows)
    record.accepted_rows_json = None
    db.commit()
    db.refresh(record)
    return record


def store_file(import_id: int, content: bytes) -> str:
    directory = settings.upload_path
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"import_{import_id}.bin"
    path.write_bytes(content)
    return str(path)


def _read_stored(record: Import) -> bytes | None:
    if not record.stored_path:
        return None
    path = Path(record.stored_path)
    if not path.exists():
        return None
    return path.read_bytes()


def remove_stored_file(record: Import) -> None:
    if record.stored_path:
        Path(record.stored_path).unlink(missing_ok=True)
