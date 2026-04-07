from app.core.errors import AppError


class ProductsService:
    def __init__(self, products_repo):
        self.products_repo = products_repo

    def _build_query(self, filters: dict, is_admin: bool):
        query = {'deletedAt': None}
        if not is_admin:
            query['active'] = True
        if filters.get('id'):
            query['_id'] = __import__('bson').ObjectId(filters['id'])
        if filters.get('text'):
            query['$or'] = [
                {'title': {'$regex': filters['text'], '$options': 'i'}},
                {'description': {'$regex': filters['text'], '$options': 'i'}},
            ]
        min_price = filters.get('minPrice')
        max_price = filters.get('maxPrice')
        if min_price is not None or max_price is not None:
            query['price'] = {}
            if min_price is not None:
                query['price']['$gte'] = float(min_price)
            if max_price is not None:
                query['price']['$lte'] = float(max_price)
        return query

    def list_or_search(self, filters: dict, is_admin: bool):
        page = int(filters.get('page', 1))
        page_size = int(filters.get('pageSize', 10))
        query = self._build_query(filters, is_admin)
        items, total = self.products_repo.list(query, page, page_size)
        return {
            'items': items,
            'meta': {
                'page': page,
                'pageSize': page_size,
                'totalItems': total,
                'totalPages': (total + page_size - 1) // page_size,
            },
        }

    def get_by_id(self, product_id: str, is_admin: bool):
        item = self.products_repo.find_by_id(product_id, include_inactive=is_admin)
        if not item:
            raise AppError(404, 'NOT_FOUND', 'Product not found')
        return item

    def create(self, payload: dict):
        return self.products_repo.create(payload)

    def update(self, product_id: str, payload: dict):
        update_payload = {k: v for k, v in payload.items() if v is not None and k not in {'id'}}
        updated = self.products_repo.update_by_id(product_id, update_payload)
        if not updated:
            raise AppError(404, 'NOT_FOUND', 'Product not found')
        return updated

    def delete(self, product_id: str, hard_delete: bool = False):
        count = self.products_repo.delete_by_id(product_id, hard_delete=hard_delete)
        if not count:
            raise AppError(404, 'NOT_FOUND', 'Product not found')
        return {'message': 'Product deleted'}
