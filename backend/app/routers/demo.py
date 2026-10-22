from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import DemoOut
from app.services import demo_service

router = APIRouter(prefix="/demo", tags=["demostracion"])


@router.post("/seed", response_model=DemoOut)
def seed(db: Session = Depends(get_db)) -> DemoOut:
    created = demo_service.seed_demo(db)
    if created == 0:
        return DemoOut(
            created=False,
            imports=0,
            sales=0,
            message="Los datos de demostración ya estaban cargados.",
        )
    return DemoOut(
        created=True,
        imports=1,
        sales=created,
        message="Datos ficticios de demostración cargados correctamente.",
    )


@router.delete("/seed", response_model=DemoOut)
def reset(db: Session = Depends(get_db)) -> DemoOut:
    removed = demo_service.reset_demo(db)
    return DemoOut(
        created=False,
        imports=removed,
        sales=0,
        message="Datos de demostración eliminados." if removed else "No había datos de demostración.",
    )
