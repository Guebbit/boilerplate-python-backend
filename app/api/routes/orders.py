from fastapi import APIRouter, Depends, Response

from app.controllers.orders import OrdersController
from app.core.dependencies import get_current_user, get_repositories, require_admin
from app.models.schemas import CreateOrderRequest, DeleteOrderRequest, SearchOrdersRequest, UpdateOrderByIdRequest, UpdateOrderRequest
from app.services.orders import OrdersService

router = APIRouter(prefix='/orders', tags=['orders'])


def get_controller(repos=Depends(get_repositories)):
    return OrdersController(OrdersService(repos['orders'], repos['products']))


@router.get('')
def list_orders(
    page: int = 1,
    pageSize: int = 10,
    id: str | None = None,
    userId: str | None = None,
    productId: str | None = None,
    email: str | None = None,
    user=Depends(get_current_user),
    controller: OrdersController = Depends(get_controller),
):
    return controller.list_or_search({'page': page, 'pageSize': pageSize, 'id': id, 'userId': userId, 'productId': productId, 'email': email}, user)


@router.post('/search')
def search_orders(payload: SearchOrdersRequest, user=Depends(get_current_user), controller: OrdersController = Depends(get_controller)):
    return controller.list_or_search(payload.model_dump(exclude_none=True), user)


@router.post('')
def create_order(payload: CreateOrderRequest, _admin=Depends(require_admin), controller: OrdersController = Depends(get_controller)):
    return controller.create(payload.model_dump())


@router.put('')
def update_order(payload: UpdateOrderRequest, _admin=Depends(require_admin), controller: OrdersController = Depends(get_controller)):
    return controller.update(payload.id, payload.model_dump(exclude_none=True))


@router.delete('')
def delete_order(payload: DeleteOrderRequest, _admin=Depends(require_admin), controller: OrdersController = Depends(get_controller)):
    return controller.delete(payload.id)


@router.get('/{id}')
def get_order_by_id(id: str, user=Depends(get_current_user), controller: OrdersController = Depends(get_controller)):
    return controller.get_by_id(id, user)


@router.put('/{id}')
def update_order_by_id(id: str, payload: UpdateOrderByIdRequest, _admin=Depends(require_admin), controller: OrdersController = Depends(get_controller)):
    return controller.update(id, payload.model_dump(exclude_none=True))


@router.delete('/{id}')
def delete_order_by_id(id: str, _admin=Depends(require_admin), controller: OrdersController = Depends(get_controller)):
    return controller.delete(id)


@router.get('/{id}/invoice')
def get_order_invoice(id: str, user=Depends(get_current_user), controller: OrdersController = Depends(get_controller)):
    controller.get_by_id(id, user)
    body = b'%PDF-1.4\n%placeholder invoice\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF'
    return Response(content=body, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename="order-{id}.pdf"'})
