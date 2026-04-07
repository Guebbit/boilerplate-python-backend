from app.core.errors import AppError


VALID_STATUSES = {'pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled'}


class OrdersService:
    def __init__(self, orders_repo, products_repo):
        self.orders_repo = orders_repo
        self.products_repo = products_repo

    def _build_query(self, filters: dict, user: dict):
        query = {}
        if filters.get('id'):
            query['_id'] = __import__('bson').ObjectId(filters['id'])
        if filters.get('userId'):
            query['userId'] = filters['userId']
        if filters.get('productId'):
            query['items.productId'] = filters['productId']
        if filters.get('email'):
            query['email'] = str(filters['email'])
        if not user.get('admin'):
            query['userId'] = user['id']
        return query

    def list_or_search(self, filters: dict, user: dict):
        page = int(filters.get('page', 1))
        page_size = int(filters.get('pageSize', 10))
        query = self._build_query(filters, user)
        items, total = self.orders_repo.list(query, page, page_size)
        return {
            'items': items,
            'meta': {
                'page': page,
                'pageSize': page_size,
                'totalItems': total,
                'totalPages': (total + page_size - 1) // page_size,
            },
        }

    def get_by_id(self, order_id: str, user: dict):
        order = self.orders_repo.find_by_id(order_id)
        if not order:
            raise AppError(404, 'NOT_FOUND', 'Order not found')
        if not user.get('admin') and order['userId'] != user['id']:
            raise AppError(403, 'FORBIDDEN', 'Order access denied')
        return order

    def create(self, payload: dict):
        normalized_items = []
        total = 0.0
        for item in payload['items']:
            product = self.products_repo.find_by_id(item['productId'], include_inactive=True)
            if not product:
                raise AppError(404, 'NOT_FOUND', f"Product {item['productId']} not found")
            quantity = int(item['quantity'])
            line_total = float(product['price']) * quantity
            total += line_total
            normalized_items.append(
                {
                    'productId': product['id'],
                    'title': product['title'],
                    'price': float(product['price']),
                    'quantity': quantity,
                }
            )

        order = {
            'userId': payload['userId'],
            'email': str(payload['email']),
            'items': normalized_items,
            'total': total,
            'status': payload.get('status', 'pending'),
            'notes': payload.get('notes'),
        }
        return self.orders_repo.create(order)

    def update(self, order_id: str, payload: dict):
        if payload.get('status') and payload['status'] not in VALID_STATUSES:
            raise AppError(422, 'VALIDATION_ERROR', 'Invalid status')
        update_payload = {k: v for k, v in payload.items() if v is not None and k != 'id'}
        updated = self.orders_repo.update_by_id(order_id, update_payload)
        if not updated:
            raise AppError(404, 'NOT_FOUND', 'Order not found')
        return updated

    def delete(self, order_id: str):
        count = self.orders_repo.delete_by_id(order_id)
        if not count:
            raise AppError(404, 'NOT_FOUND', 'Order not found')
        return {'message': 'Order deleted'}
