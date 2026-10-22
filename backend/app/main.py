from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import AppError, app_error_handler, generic_error_handler
from app.models import Import, Sale  # noqa: F401 - registra los modelos
from app.routers import analytics, demo, health, imports, reports, sales


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API para analizar ventas, ingresos y rendimiento comercial a partir de archivos CSV/Excel.",
        lifespan=lifespan,
        contact={"name": "Business Analytics Dashboard"},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, _validation_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    api_prefix = "/api"
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(imports.router, prefix=api_prefix)
    app.include_router(sales.router, prefix=api_prefix)
    app.include_router(analytics.router, prefix=api_prefix)
    app.include_router(reports.router, prefix=api_prefix)
    app.include_router(demo.router, prefix=api_prefix)

    @app.get("/", tags=["estado"])
    def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/health",
        }

    return app


async def _validation_handler(request, exc):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=422, content={"detail": "Parámetros de consulta inválidos."})


app = create_app()
