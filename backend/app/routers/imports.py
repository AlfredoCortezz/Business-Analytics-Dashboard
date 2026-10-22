from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.repositories import imports_repo
from app.schemas import ImportDetail, ImportErrorItem, ImportOut, Paginated
from app.services import import_service

router = APIRouter(prefix="/imports", tags=["importaciones"])


@router.post("", response_model=ImportDetail, status_code=201)
async def create_import(file: UploadFile = File(...), db: Session = Depends(get_db)) -> ImportDetail:
    content = await file.read()
    record = import_service.create_pending_import(db, file.filename or "", content)
    try:
        record.stored_path = import_service.store_file(record.id, content)
        record = imports_repo.save(db, record)
    except OSError:
        # El disco puede ser efímero o de solo lectura (p. ej. en la nube).
        # Las filas aceptadas ya están guardadas en la base de datos, así que
        # la confirmación funciona igualmente.
        pass
    return _to_detail(record)


@router.get("", response_model=Paginated[ImportOut])
def list_imports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> Paginated[ImportOut]:
    items, total = imports_repo.list_paginated(db, page=page, page_size=page_size)
    return Paginated[ImportOut](
        items=[ImportOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{import_id}", response_model=ImportDetail)
def get_import(import_id: int, db: Session = Depends(get_db)) -> ImportDetail:
    record = imports_repo.get(db, import_id)
    if record is None:
        raise NotFoundError("Importación no encontrada.")
    return _to_detail(record)


@router.post("/{import_id}/confirm", response_model=ImportDetail)
def confirm_import(import_id: int, db: Session = Depends(get_db)) -> ImportDetail:
    record = import_service.confirm_import(db, import_id)
    return _to_detail(record)


@router.delete("/{import_id}", status_code=204)
def delete_import(import_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    record = imports_repo.get(db, import_id)
    if record is None:
        raise NotFoundError("Importación no encontrada.")
    import_service.remove_stored_file(record)
    imports_repo.delete(db, record)
    return JSONResponse(status_code=204, content=None)


def _to_detail(record) -> ImportDetail:
    errors = [ImportErrorItem(**item) for item in (record.errors_json or [])]
    return ImportDetail(
        id=record.id,
        filename=record.filename,
        status=record.status,
        total_rows=record.total_rows,
        accepted_rows=record.accepted_rows,
        rejected_rows=record.rejected_rows,
        duplicate_rows=record.duplicate_rows,
        is_demo=record.is_demo,
        created_at=record.created_at,
        confirmed_at=record.confirmed_at,
        errors=errors,
    )
