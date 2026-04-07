from datetime import datetime, timezone
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    generate_reset_token,
    hash_password,
    verify_password,
)
from app.core.dependencies import refresh_expiration, reset_expiration


class AuthService:
    def __init__(self, users_repo):
        self.users_repo = users_repo

    def _sanitize_user(self, user: dict) -> dict:
        user = dict(user)
        user.pop('passwordHash', None)
        user.pop('tokens', None)
        return user

    def get_account(self, user: dict):
        return self._sanitize_user(user)

    def signup(self, payload: dict):
        if payload['password'] != payload['passwordConfirm']:
            raise AppError(422, 'VALIDATION_ERROR', 'Passwords do not match')

        existing = self.users_repo.find_by_email(payload['email'])
        if existing:
            raise AppError(422, 'USER_EXISTS', 'Email already registered')

        user = self.users_repo.create(
            {
                'email': payload['email'],
                'username': payload['username'],
                'passwordHash': hash_password(payload['password']),
                'admin': False,
                'active': True,
                'imageUrl': payload.get('imageUrl'),
            }
        )
        return self._sanitize_user(user)

    def login(self, email: str, password: str):
        user = self.users_repo.find_by_email(email)
        if not user or not verify_password(password, user['passwordHash']):
            raise AppError(401, 'AUTH_INVALID_CREDENTIALS', 'Invalid credentials')
        if not user.get('active', True):
            raise AppError(403, 'AUTH_USER_DISABLED', 'User disabled')

        settings = get_settings()
        access_token = create_access_token(user['id'], bool(user.get('admin')), settings.access_token_secret, settings.access_token_expire_minutes)
        refresh_token = generate_refresh_token()

        tokens = user.get('tokens', [])
        tokens.append(
            {
                'type': 'refresh',
                'token': refresh_token,
                'expiration': refresh_expiration(),
            }
        )
        self.users_repo.update_by_id(user['id'], {'tokens': tokens})
        return {'token': access_token, 'refreshToken': refresh_token, 'expiresIn': settings.access_token_expire_minutes * 60}

    def request_reset(self, email: str):
        user = self.users_repo.find_by_email(email)
        if user:
            tokens = user.get('tokens', [])
            tokens.append(
                {
                    'type': 'password-reset',
                    'token': generate_reset_token(),
                    'expiration': reset_expiration(),
                }
            )
            self.users_repo.update_by_id(user['id'], {'tokens': tokens})
        return {'message': 'Password reset requested'}

    def confirm_reset(self, token: str, password: str, password_confirm: str):
        if password != password_confirm:
            raise AppError(422, 'VALIDATION_ERROR', 'Passwords do not match')

        now = datetime.now(timezone.utc)
        found_user = self.users_repo.find_by_active_token('password-reset', token, now)

        if not found_user:
            raise AppError(401, 'AUTH_INVALID_TOKEN', 'Invalid or expired reset token')

        filtered_tokens = [t for t in found_user.get('tokens', []) if t.get('token') != token]
        self.users_repo.update_by_id(
            found_user['id'],
            {'passwordHash': hash_password(password), 'tokens': filtered_tokens},
        )
        return {'message': 'Password updated'}

    def refresh(self, token: str):
        now = datetime.now(timezone.utc)
        owner = self.users_repo.find_by_active_token('refresh', token, now)

        if not owner:
            raise AppError(401, 'AUTH_INVALID_TOKEN', 'Invalid refresh token')

        settings = get_settings()
        access_token = create_access_token(owner['id'], bool(owner.get('admin')), settings.access_token_secret, settings.access_token_expire_minutes)
        return {'token': access_token, 'refreshToken': token, 'expiresIn': settings.access_token_expire_minutes * 60}

    def logout_all(self, user_id: str):
        self.users_repo.update_by_id(user_id, {'tokens': []})
        return {'message': 'Logged out'}

    def delete_expired_tokens(self):
        count = self.users_repo.remove_expired_tokens(datetime.now(timezone.utc))
        return {'removedUsers': count}
