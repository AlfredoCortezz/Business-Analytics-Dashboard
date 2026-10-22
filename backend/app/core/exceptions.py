from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(AppError):
    def __init__(self, detail: str = "Recurso no encontrado."):
        super().__init__(detail, status_code=404)


class ConflictError(AppError):
    def __init__(self, detail: str = "Conflicto con el estado actual del recurso."):
        super().__init__(detail, status_code=409)


class PayloadTooLargeError(AppError):
    def __init__(self, detail: str = "El archivo supera el tamaño máximo permitido."):
        super().__init__(detail, status_code=413)


class UnsupportedMediaError(AppError):
    def __init__(self, detail: str = "Tipo de archivo no admitido. Use CSV o Excel (.xlsx)."):
        super().__init__(detail, status_code=415)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": "Los datos enviados no son válidos."})


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor."})
