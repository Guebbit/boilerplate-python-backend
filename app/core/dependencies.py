from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories.users import UsersRepository
from app.repositories.products import ProductsRepository
from app.repositories.orders import OrdersRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_repositories():
    db = get_db()
    return {
        'users': UsersRepository(db.users),
        'products': ProductsRepository(db.products),
        'orders': OrdersRepository(db.orders),
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repos=Depends(get_repositories),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    settings = get_settings()
    try:
        payload = decode_access_token(credentials.credentials, settings.access_token_secret)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail='Unauthorized') from exc

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')

    user = repos['users'].find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')

    return user


def require_admin(user=Depends(get_current_user)):
    if not user.get('admin'):
        raise HTTPException(status_code=403, detail='Forbidden')
    return user


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def refresh_expiration() -> datetime:
    settings = get_settings()
    return now_utc() + timedelta(days=settings.refresh_token_expire_days)


def reset_expiration() -> datetime:
    settings = get_settings()
    return now_utc() + timedelta(minutes=settings.reset_token_expire_minutes)


def get_request_id(request: Request) -> str:
    return getattr(request.state, 'request_id', 'unknown')
