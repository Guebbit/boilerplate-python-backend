from typing import Any
from fastapi.responses import JSONResponse


def success_response(status_code: int, message: str, data: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            'success': True,
            'status': status_code,
            'message': message,
            'data': data,
        },
    )


def error_response(status_code: int, message: str, errors: list[str] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            'success': False,
            'status': status_code,
            'message': message,
            'errors': errors or [],
        },
    )
