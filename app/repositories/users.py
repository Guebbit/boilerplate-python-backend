from datetime import datetime, timezone
from pymongo.collection import Collection
from app.repositories.base import normalize_id, to_object_id


class UsersRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def find_by_email(self, email: str):
        return normalize_id(self.collection.find_one({'email': email, 'deletedAt': None}))

    def find_by_id(self, user_id: str):
        return normalize_id(self.collection.find_one({'_id': to_object_id(user_id), 'deletedAt': None}))

    def create(self, payload: dict):
        now = datetime.now(timezone.utc)
        payload.setdefault('admin', False)
        payload.setdefault('active', True)
        payload.setdefault('cart', [])
        payload.setdefault('tokens', [])
        payload['deletedAt'] = None
        payload['createdAt'] = now
        payload['updatedAt'] = now
        result = self.collection.insert_one(payload)
        return self.find_by_id(str(result.inserted_id))

    def update_by_id(self, user_id: str, payload: dict):
        payload['updatedAt'] = datetime.now(timezone.utc)
        self.collection.update_one({'_id': to_object_id(user_id)}, {'$set': payload})
        return self.find_by_id(user_id)

    def delete_by_id(self, user_id: str, hard_delete: bool = False):
        if hard_delete:
            return self.collection.delete_one({'_id': to_object_id(user_id)}).deleted_count
        return self.collection.update_one(
            {'_id': to_object_id(user_id)},
            {'$set': {'deletedAt': datetime.now(timezone.utc), 'updatedAt': datetime.now(timezone.utc)}},
        ).modified_count

    def list(self, query: dict, page: int, page_size: int):
        cursor = self.collection.find(query).skip((page - 1) * page_size).limit(page_size)
        items = [normalize_id(item) for item in cursor]
        total = self.collection.count_documents(query)
        return items, total

    def remove_expired_tokens(self, now: datetime):
        result = self.collection.update_many({}, {'$pull': {'tokens': {'expiration': {'$lte': now}}}})
        return result.modified_count
