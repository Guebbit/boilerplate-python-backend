from app.core.responses import success_response
from app.services.users import UsersService


class UsersController:
    def __init__(self, service: UsersService):
        self.service = service

    def list_or_search(self, filters: dict):
        return success_response(200, 'USERS_FETCHED', self.service.list_or_search(filters))

    def get_by_id(self, user_id: str):
        return success_response(200, 'USER_FETCHED', self.service.get_by_id(user_id))

    def create(self, payload: dict):
        return success_response(201, 'USER_CREATED', self.service.create(payload))

    def update(self, user_id: str, payload: dict):
        return success_response(200, 'USER_UPDATED', self.service.update(user_id, payload))

    def delete(self, user_id: str, hard_delete: bool):
        return success_response(200, 'USER_DELETED', self.service.delete(user_id, hard_delete))
