from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.controllers.products import ProductsController
from app.core.dependencies import get_current_user, get_repositories, require_admin
from app.models.schemas import DeleteProductRequest, SearchProductsRequest, UpdateProductByIdRequest, UpdateProductRequest
from app.services.products import ProductsService

router = APIRouter(prefix='/products', tags=['products'])
optional_bearer = HTTPBearer(auto_error=False)


def get_controller(repos=Depends(get_repositories)):
    return ProductsController(ProductsService(repos['products']))


def is_admin_optional(credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer), repos=Depends(get_repositories)) -> bool:
    if not credentials:
        return False
    try:
        user = get_current_user(credentials=credentials, repos=repos)
        return bool(user.get('admin'))
    except Exception:  # noqa: BLE001
        return False


@router.get('')
def list_products(
    page: int = 1,
    pageSize: int = 10,
    text: str | None = None,
    id: str | None = None,
    minPrice: float | None = None,
    maxPrice: float | None = None,
    is_admin: bool = Depends(is_admin_optional),
    controller: ProductsController = Depends(get_controller),
):
    return controller.list_or_search({'page': page, 'pageSize': pageSize, 'text': text, 'id': id, 'minPrice': minPrice, 'maxPrice': maxPrice}, is_admin)


@router.post('/search')
def search_products(payload: SearchProductsRequest, is_admin: bool = Depends(is_admin_optional), controller: ProductsController = Depends(get_controller)):
    return controller.list_or_search(payload.model_dump(exclude_none=True), is_admin)


@router.get('/{id}')
def get_product_by_id(id: str, is_admin: bool = Depends(is_admin_optional), controller: ProductsController = Depends(get_controller)):
    return controller.get_by_id(id, is_admin)


@router.post('')
def create_product(
    title: str = Form(...),
    price: float = Form(...),
    description: str | None = Form(default=None),
    active: bool = Form(default=True),
    imageUpload: UploadFile | None = File(default=None),
    _admin=Depends(require_admin),
    controller: ProductsController = Depends(get_controller),
):
    image_url = f'/uploads/{imageUpload.filename}' if imageUpload else None
    return controller.create({'title': title, 'price': price, 'description': description, 'active': active, 'imageUrl': image_url})


@router.put('')
def update_product(
    id: str = Form(...),
    title: str = Form(...),
    price: float = Form(...),
    description: str | None = Form(default=None),
    active: bool | None = Form(default=None),
    imageUpload: UploadFile | None = File(default=None),
    _admin=Depends(require_admin),
    controller: ProductsController = Depends(get_controller),
):
    image_url = f'/uploads/{imageUpload.filename}' if imageUpload else None
    payload = UpdateProductRequest(id=id, title=title, price=price, description=description, active=active, imageUrl=image_url)
    return controller.update(payload.id, payload.model_dump(exclude_none=True))


@router.delete('')
def delete_product(payload: DeleteProductRequest, _admin=Depends(require_admin), controller: ProductsController = Depends(get_controller)):
    return controller.delete(payload.id, payload.hardDelete)


@router.put('/{id}')
def update_product_by_id(
    id: str,
    title: str = Form(...),
    price: float = Form(...),
    description: str | None = Form(default=None),
    active: bool | None = Form(default=None),
    imageUpload: UploadFile | None = File(default=None),
    _admin=Depends(require_admin),
    controller: ProductsController = Depends(get_controller),
):
    image_url = f'/uploads/{imageUpload.filename}' if imageUpload else None
    payload = UpdateProductByIdRequest(title=title, price=price, description=description, active=active, imageUrl=image_url)
    return controller.update(id, payload.model_dump(exclude_none=True))


@router.delete('/{id}')
def delete_product_by_id(id: str, hardDelete: bool = False, _admin=Depends(require_admin), controller: ProductsController = Depends(get_controller)):
    return controller.delete(id, hardDelete)
