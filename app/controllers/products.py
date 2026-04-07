from app.core.responses import success_response
from app.services.products import ProductsService


class ProductsController:
    def __init__(self, service: ProductsService):
        self.service = service

    def list_or_search(self, filters: dict, is_admin: bool):
        return success_response(200, 'PRODUCTS_FETCHED', self.service.list_or_search(filters, is_admin))

    def get_by_id(self, product_id: str, is_admin: bool):
        return success_response(200, 'PRODUCT_FETCHED', self.service.get_by_id(product_id, is_admin))

    def create(self, payload: dict):
        return success_response(201, 'PRODUCT_CREATED', self.service.create(payload))

    def update(self, product_id: str, payload: dict):
        return success_response(200, 'PRODUCT_UPDATED', self.service.update(product_id, payload))

    def delete(self, product_id: str, hard_delete: bool):
        return success_response(200, 'PRODUCT_DELETED', self.service.delete(product_id, hard_delete))
