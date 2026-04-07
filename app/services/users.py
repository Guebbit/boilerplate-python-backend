from app.core.errors import AppError
from app.core.security import hash_password


class UsersService:
    def __init__(self, users_repo):
        self.users_repo = users_repo

    def _sanitize(self, user: dict):
        user = dict(user)
        user.pop('passwordHash', None)
        user.pop('tokens', None)
        return user

    def _build_query(self, filters: dict):
        query = {'deletedAt': None}
        if filters.get('id'):
            query['_id'] = __import__('bson').ObjectId(filters['id'])
        if filters.get('email'):
            query['email'] = str(filters['email'])
        if filters.get('username'):
            query['username'] = {'$regex': filters['username'], '$options': 'i'}
        if filters.get('active') is not None:
            query['active'] = filters['active']
        if filters.get('text'):
            query['$or'] = [
                {'email': {'$regex': filters['text'], '$options': 'i'}},
                {'username': {'$regex': filters['text'], '$options': 'i'}},
            ]
        return query

    def list_or_search(self, filters: dict):
        page = int(filters.get('page', 1))
        page_size = int(filters.get('pageSize', 10))
        query = self._build_query(filters)
        items, total = self.users_repo.list(query, page, page_size)
        return {
            'items': [self._sanitize(i) for i in items],
            'meta': {
                'page': page,
                'pageSize': page_size,
                'totalItems': total,
                'totalPages': (total + page_size - 1) // page_size,
            },
        }

    def get_by_id(self, user_id: str):
        user = self.users_repo.find_by_id(user_id)
        if not user:
            raise AppError(404, 'NOT_FOUND', 'User not found')
        return self._sanitize(user)

    def create(self, payload: dict):
        if self.users_repo.find_by_email(payload['email']):
            raise AppError(422, 'USER_EXISTS', 'Email already registered')

        user = self.users_repo.create(
            {
                'email': str(payload['email']),
                'username': payload['username'],
                'passwordHash': hash_password(payload['password']),
                'admin': bool(payload.get('admin', False)),
                'active': bool(payload.get('active', True)),
                'imageUrl': payload.get('imageUrl'),
            }
        )
        return self._sanitize(user)

    def update(self, user_id: str, payload: dict):
        update_payload = {k: v for k, v in payload.items() if v is not None and k not in {'id'}}
        if 'password' in update_payload:
            update_payload['passwordHash'] = hash_password(update_payload.pop('password'))
        updated = self.users_repo.update_by_id(user_id, update_payload)
        if not updated:
            raise AppError(404, 'NOT_FOUND', 'User not found')
        return self._sanitize(updated)

    def delete(self, user_id: str, hard_delete: bool = False):
        count = self.users_repo.delete_by_id(user_id, hard_delete=hard_delete)
        if not count:
            raise AppError(404, 'NOT_FOUND', 'User not found')
        return {'message': 'User deleted'}
