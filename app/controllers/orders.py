from app.core.responses import success_response
from app.services.orders import OrdersService


class OrdersController:
    def __init__(self, service: OrdersService):
        self.service = service

    def list_or_search(self, filters: dict, user: dict):
        return success_response(200, 'ORDERS_FETCHED', self.service.list_or_search(filters, user))

    def get_by_id(self, order_id: str, user: dict):
        return success_response(200, 'ORDER_FETCHED', self.service.get_by_id(order_id, user))

    def create(self, payload: dict):
        return success_response(201, 'ORDER_CREATED', self.service.create(payload))

    def update(self, order_id: str, payload: dict):
        return success_response(200, 'ORDER_UPDATED', self.service.update(order_id, payload))

    def delete(self, order_id: str):
        return success_response(200, 'ORDER_DELETED', self.service.delete(order_id))
