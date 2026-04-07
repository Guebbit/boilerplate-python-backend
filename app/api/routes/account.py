from fastapi import APIRouter, Cookie, Depends, Form, Response, UploadFile, File

from app.controllers.account import AccountController
from app.core.dependencies import get_current_user, get_repositories, require_admin
from app.core.errors import AppError
from app.models.schemas import LoginRequest, PasswordResetConfirmRequest, PasswordResetRequest
from app.services.auth import AuthService

router = APIRouter(prefix='/account', tags=['account'])


def get_controller(repos=Depends(get_repositories)):
    return AccountController(AuthService(repos['users']))


@router.get('')
def get_account(user=Depends(get_current_user), controller: AccountController = Depends(get_controller)):
    return controller.get_account(user)


@router.post('/login')
def login(payload: LoginRequest, response: Response, controller: AccountController = Depends(get_controller)):
    return controller.login(payload.model_dump(), response)


@router.post('/signup')
def signup(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    passwordConfirm: str = Form(...),
    imageUpload: UploadFile | None = File(default=None),
    controller: AccountController = Depends(get_controller),
):
    image_url = f'/uploads/{imageUpload.filename}' if imageUpload else None
    return controller.signup(
        {
            'email': email,
            'username': username,
            'password': password,
            'passwordConfirm': passwordConfirm,
            'imageUrl': image_url,
        }
    )


@router.post('/reset')
def reset(payload: PasswordResetRequest, controller: AccountController = Depends(get_controller)):
    return controller.reset(str(payload.email))


@router.post('/reset-confirm')
def reset_confirm(payload: PasswordResetConfirmRequest, controller: AccountController = Depends(get_controller)):
    return controller.reset_confirm(payload.token, payload.password, payload.passwordConfirm)


@router.get('/refresh')
def refresh(
    response: Response,
    jwt: str | None = Cookie(default=None),
    token: str | None = None,
    controller: AccountController = Depends(get_controller),
):
    refresh_token = token or jwt
    if not refresh_token:
        raise AppError(401, 'AUTH_INVALID_TOKEN', 'Refresh token missing')
    return controller.refresh(refresh_token, response)


@router.get('/refresh/{token}')
def refresh_with_path(token: str, response: Response, controller: AccountController = Depends(get_controller)):
    return controller.refresh(token, response)


@router.post('/logout-all')
def logout_all(response: Response, user=Depends(get_current_user), controller: AccountController = Depends(get_controller)):
    return controller.logout_all(user['id'], response)


@router.delete('/tokens/expired')
def delete_expired_tokens(
    _admin=Depends(require_admin),
    controller: AccountController = Depends(get_controller),
):
    return controller.delete_expired_tokens()
