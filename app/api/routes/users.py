from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.controllers.users import UsersController
from app.core.dependencies import get_repositories, require_admin
from app.models.schemas import DeleteUserRequest, SearchUsersRequest, UpdateUserRequest, UpdateUserByIdRequest
from app.services.users import UsersService

router = APIRouter(prefix='/users', tags=['users'])


def get_controller(repos=Depends(get_repositories)):
    return UsersController(UsersService(repos['users']))


@router.get('')
def list_users(
    page: int = 1,
    pageSize: int = 10,
    text: str | None = None,
    id: str | None = None,
    email: str | None = None,
    username: str | None = None,
    active: bool | None = None,
    _admin=Depends(require_admin),
    controller: UsersController = Depends(get_controller),
):
    return controller.list_or_search({'page': page, 'pageSize': pageSize, 'text': text, 'id': id, 'email': email, 'username': username, 'active': active})


@router.post('/search')
def search_users(payload: SearchUsersRequest, _admin=Depends(require_admin), controller: UsersController = Depends(get_controller)):
    return controller.list_or_search(payload.model_dump(exclude_none=True))


@router.post('')
def create_user(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    admin: bool = Form(default=False),
    active: bool = Form(default=True),
    imageUpload: UploadFile | None = File(default=None),
    _admin=Depends(require_admin),
    controller: UsersController = Depends(get_controller),
):
    image_url = f'/uploads/{imageUpload.filename}' if imageUpload else None
    return controller.create({'email': email, 'username': username, 'password': password, 'admin': admin, 'active': active, 'imageUrl': image_url})


@router.put('')
def update_user(
    id: str = Form(...),
    email: str | None = Form(default=None),
    username: str | None = Form(default=None),
    password: str | None = Form(default=None),
    imageUpload: UploadFile | None = File(default=None),
    _admin=Depends(require_admin),
    controller: UsersController = Depends(get_controller),
):
    image_url = f'/uploads/{imageUpload.filename}' if imageUpload else None
    payload = UpdateUserRequest(id=id, email=email, username=username, password=password, imageUrl=image_url)
    return controller.update(payload.id, payload.model_dump(exclude_none=True))


@router.delete('')
def delete_user(payload: DeleteUserRequest, _admin=Depends(require_admin), controller: UsersController = Depends(get_controller)):
    return controller.delete(payload.id, payload.hardDelete)


@router.get('/{id}')
def get_user_by_id(id: str, _admin=Depends(require_admin), controller: UsersController = Depends(get_controller)):
    return controller.get_by_id(id)


@router.put('/{id}')
def update_user_by_id(
    id: str,
    email: str | None = Form(default=None),
    username: str | None = Form(default=None),
    password: str | None = Form(default=None),
    imageUpload: UploadFile | None = File(default=None),
    _admin=Depends(require_admin),
    controller: UsersController = Depends(get_controller),
):
    image_url = f'/uploads/{imageUpload.filename}' if imageUpload else None
    payload = UpdateUserByIdRequest(email=email, username=username, password=password, imageUrl=image_url)
    return controller.update(id, payload.model_dump(exclude_none=True))


@router.delete('/{id}')
def delete_user_by_id(id: str, hardDelete: bool = False, _admin=Depends(require_admin), controller: UsersController = Depends(get_controller)):
    return controller.delete(id, hardDelete)
