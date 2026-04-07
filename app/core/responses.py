from typing import Any
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(status_code: int, message: str, data: Any = None) -> JSONResponse:
    payload = jsonable_encoder(
        {
            'success': True,
            'status': status_code,
            'message': message,
            'data': data,
        }
    )
    return JSONResponse(
        status_code=status_code,
        content=payload,
    )


def error_response(status_code: int, message: str, errors: list[str] | None = None) -> JSONResponse:
    payload = jsonable_encoder(
        {
            'success': False,
            'status': status_code,
            'message': message,
            'errors': errors or [],
        }
    )
    return JSONResponse(
        status_code=status_code,
        content=payload,
    )
