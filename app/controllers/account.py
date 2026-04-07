from fastapi import Response

from app.core.responses import success_response
from app.services.auth import AuthService


class AccountController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def get_account(self, user: dict):
        return success_response(200, 'ACCOUNT_FETCHED', self.auth_service.get_account(user))

    def signup(self, payload: dict):
        return success_response(201, 'ACCOUNT_CREATED', self.auth_service.signup(payload))

    def login(self, payload: dict, response: Response):
        data = self.auth_service.login(payload['email'], payload['password'])
        response.set_cookie('jwt', data['refreshToken'], httponly=True, samesite='lax')
        return success_response(200, 'AUTH_LOGIN_SUCCESS', data)

    def reset(self, email: str):
        return success_response(200, 'AUTH_RESET_REQUESTED', self.auth_service.request_reset(email))

    def reset_confirm(self, token: str, password: str, password_confirm: str):
        return success_response(200, 'AUTH_RESET_CONFIRMED', self.auth_service.confirm_reset(token, password, password_confirm))

    def refresh(self, token: str, response: Response):
        data = self.auth_service.refresh(token)
        response.set_cookie('jwt', data['refreshToken'], httponly=True, samesite='lax')
        return success_response(200, 'AUTH_REFRESHED', data)

    def logout_all(self, user_id: str, response: Response):
        data = self.auth_service.logout_all(user_id)
        response.delete_cookie('jwt')
        return success_response(200, 'AUTH_LOGOUT_ALL', data)

    def delete_expired_tokens(self):
        return success_response(200, 'AUTH_TOKENS_CLEANED', self.auth_service.delete_expired_tokens())
