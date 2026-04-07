from fastapi import APIRouter, Body, Depends

from app.controllers.cart import CartController
from app.core.dependencies import get_current_user, get_repositories
from app.models.schemas import CartItemRequest, CheckoutRequest, RemoveCartItemRequest, UpdateCartItemByIdRequest
from app.services.cart import CartService
from app.services.orders import OrdersService

router = APIRouter(prefix='/cart', tags=['cart'])


def get_controller(repos=Depends(get_repositories)):
    orders_service = OrdersService(repos['orders'], repos['products'])
    return CartController(CartService(repos['users'], repos['products'], orders_service))


@router.get('')
def get_cart(user=Depends(get_current_user), controller: CartController = Depends(get_controller)):
    return controller.get_cart(user)


@router.post('')
def upsert_cart_item(payload: CartItemRequest, user=Depends(get_current_user), controller: CartController = Depends(get_controller)):
    return controller.upsert(user, payload.productId, payload.quantity)


@router.delete('')
def clear_or_remove_cart(payload: RemoveCartItemRequest | None = Body(default=None), user=Depends(get_current_user), controller: CartController = Depends(get_controller)):
    product_id = payload.productId if payload else None
    return controller.remove(user, product_id)


@router.put('/{productId}')
def update_cart_item_by_id(productId: str, payload: UpdateCartItemByIdRequest, user=Depends(get_current_user), controller: CartController = Depends(get_controller)):
    return controller.upsert(user, productId, payload.quantity)


@router.delete('/{productId}')
def remove_cart_item(productId: str, user=Depends(get_current_user), controller: CartController = Depends(get_controller)):
    return controller.remove(user, productId)


@router.get('/summary')
def get_cart_summary(user=Depends(get_current_user), controller: CartController = Depends(get_controller)):
    return controller.summary(user)


@router.post('/checkout')
def checkout(payload: CheckoutRequest | None = None, user=Depends(get_current_user), controller: CartController = Depends(get_controller)):
    return controller.checkout(user, str(payload.email) if payload and payload.email else None, payload.notes if payload else None)
