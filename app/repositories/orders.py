from datetime import datetime, timezone
from pymongo.collection import Collection
from app.repositories.base import normalize_id, to_object_id


class OrdersRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, payload: dict):
        now = datetime.now(timezone.utc)
        payload['createdAt'] = now
        payload['updatedAt'] = now
        result = self.collection.insert_one(payload)
        return self.find_by_id(str(result.inserted_id))

    def find_by_id(self, order_id: str):
        return normalize_id(self.collection.find_one({'_id': to_object_id(order_id)}))

    def update_by_id(self, order_id: str, payload: dict):
        payload['updatedAt'] = datetime.now(timezone.utc)
        self.collection.update_one({'_id': to_object_id(order_id)}, {'$set': payload})
        return self.find_by_id(order_id)

    def delete_by_id(self, order_id: str):
        return self.collection.delete_one({'_id': to_object_id(order_id)}).deleted_count

    def list(self, query: dict, page: int, page_size: int):
        cursor = self.collection.find(query).skip((page - 1) * page_size).limit(page_size)
        items = [normalize_id(item) for item in cursor]
        total = self.collection.count_documents(query)
        return items, total
