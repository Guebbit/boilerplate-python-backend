from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

from app.api.routes.account import router as account_router
from app.api.routes.cart import router as cart_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.products import router as products_router
from app.api.routes.users import router as users_router
from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import AppError
from app.core.middleware import RequestIdMiddleware, SecurityHeadersMiddleware, SimpleRateLimitMiddleware
from app.core.responses import error_response
from app.repositories.users import UsersRepository

settings = get_settings()
app = FastAPI(title=settings.app_name, version='1.0.0')

app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SimpleRateLimitMiddleware)


@app.on_event('startup')
def startup_event():
    db = get_db()
    UsersRepository(db.users).remove_expired_tokens(datetime.now(timezone.utc))


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return error_response(exc.status_code, exc.code, [exc.message])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    message = 'UNAUTHORIZED' if exc.status_code == 401 else 'FORBIDDEN' if exc.status_code == 403 else 'HTTP_ERROR'
    return error_response(exc.status_code, message, [str(exc.detail)])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" for err in exc.errors()]
    return error_response(422, 'VALIDATION_ERROR', errors)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return error_response(500, 'INTERNAL_SERVER_ERROR', ['Unexpected server error'])


app.include_router(health_router)
app.include_router(account_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
