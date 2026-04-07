from app.core.errors import AppError


class CartService:
    def __init__(self, users_repo, products_repo, orders_service):
        self.users_repo = users_repo
        self.products_repo = products_repo
        self.orders_service = orders_service

    def _resolve_cart_items(self, cart_items: list[dict], include_inactive: bool):
        items = []
        for line in cart_items:
            product = self.products_repo.find_by_id(line['productId'], include_inactive=include_inactive)
            if product:
                items.append({'productId': line['productId'], 'quantity': int(line['quantity']), 'price': float(product['price'])})
        return items

    def _summary(self, resolved_items: list[dict]):
        items_count = len(resolved_items)
        total_quantity = sum(item['quantity'] for item in resolved_items)
        total = sum(item['quantity'] * item['price'] for item in resolved_items)
        return {
            'itemsCount': items_count,
            'totalQuantity': total_quantity,
            'total': total,
            'currency': 'USD',
        }

    def get_cart(self, user: dict):
        cart_items = user.get('cart', [])
        resolved = self._resolve_cart_items(cart_items, include_inactive=False)
        payload = {'items': [{'productId': i['productId'], 'quantity': i['quantity']} for i in resolved], 'summary': self._summary(resolved)}
        return payload

    def upsert_item(self, user: dict, product_id: str, quantity: int):
        product = self.products_repo.find_by_id(product_id, include_inactive=False)
        if not product:
            raise AppError(404, 'NOT_FOUND', 'Product not found')

        cart = user.get('cart', [])
        found = False
        for item in cart:
            if item['productId'] == product_id:
                item['quantity'] = quantity
                found = True
                break
        if not found:
            cart.append({'productId': product_id, 'quantity': quantity})

        updated = self.users_repo.update_by_id(user['id'], {'cart': cart})
        return self.get_cart(updated)

    def remove_item(self, user: dict, product_id: str | None = None):
        if product_id:
            cart = [item for item in user.get('cart', []) if item['productId'] != product_id]
        else:
            cart = []
        updated = self.users_repo.update_by_id(user['id'], {'cart': cart})
        return self.get_cart(updated)

    def checkout(self, user: dict, email: str | None = None, notes: str | None = None):
        cart_lines = user.get('cart', [])
        if not cart_lines:
            raise AppError(422, 'VALIDATION_ERROR', 'Cart is empty')

        order = self.orders_service.create(
            {
                'userId': user['id'],
                'email': email or user['email'],
                'items': cart_lines,
                'notes': notes,
                'status': 'pending',
            }
        )
        self.users_repo.update_by_id(user['id'], {'cart': []})
        return {'order': order, 'message': 'Checkout completed'}
