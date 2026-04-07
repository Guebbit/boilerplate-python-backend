from app.core.responses import success_response
from app.services.cart import CartService


class CartController:
    def __init__(self, service: CartService):
        self.service = service

    def get_cart(self, user: dict):
        return success_response(200, 'CART_FETCHED', self.service.get_cart(user))

    def upsert(self, user: dict, product_id: str, quantity: int):
        return success_response(200, 'CART_UPDATED', self.service.upsert_item(user, product_id, quantity))

    def remove(self, user: dict, product_id: str | None = None):
        return success_response(200, 'CART_UPDATED', self.service.remove_item(user, product_id))

    def summary(self, user: dict):
        cart = self.service.get_cart(user)
        return success_response(200, 'CART_SUMMARY', cart['summary'])

    def checkout(self, user: dict, email: str | None = None, notes: str | None = None):
        return success_response(201, 'CHECKOUT_COMPLETED', self.service.checkout(user, email, notes))
