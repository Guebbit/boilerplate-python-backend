from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)
    passwordConfirm: str = Field(min_length=8)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    password: str = Field(min_length=8)
    passwordConfirm: str = Field(min_length=8)


class PaginationRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=100)


class SearchUsersRequest(PaginationRequest):
    text: Optional[str] = None
    id: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    active: Optional[bool] = None


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(min_length=8)
    admin: bool = False
    active: bool = True
    imageUrl: Optional[str] = None


class UpdateUserRequest(BaseModel):
    id: str
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)
    imageUrl: Optional[str] = None


class UpdateUserByIdRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)
    imageUrl: Optional[str] = None


class DeleteUserRequest(BaseModel):
    id: str
    hardDelete: bool = False


class SearchProductsRequest(PaginationRequest):
    text: Optional[str] = None
    id: Optional[str] = None
    minPrice: Optional[float] = Field(default=None, ge=0)
    maxPrice: Optional[float] = Field(default=None, ge=0)


class CreateProductRequest(BaseModel):
    title: str
    price: float = Field(ge=0)
    description: Optional[str] = None
    active: bool = True
    imageUrl: Optional[str] = None


class UpdateProductRequest(BaseModel):
    id: str
    title: str
    price: float = Field(ge=0)
    description: Optional[str] = None
    active: Optional[bool] = None
    imageUrl: Optional[str] = None


class UpdateProductByIdRequest(BaseModel):
    title: str
    price: float = Field(ge=0)
    description: Optional[str] = None
    active: Optional[bool] = None
    imageUrl: Optional[str] = None


class DeleteProductRequest(BaseModel):
    id: str
    hardDelete: bool = False


class CartItemRequest(BaseModel):
    productId: str
    quantity: int = Field(ge=1)


class UpdateCartItemByIdRequest(BaseModel):
    quantity: int = Field(ge=1)


class RemoveCartItemRequest(BaseModel):
    productId: Optional[str] = None


class CheckoutRequest(BaseModel):
    email: Optional[EmailStr] = None
    notes: Optional[str] = None


class SearchOrdersRequest(PaginationRequest):
    id: Optional[str] = None
    userId: Optional[str] = None
    productId: Optional[str] = None
    email: Optional[EmailStr] = None


class CreateOrderRequest(BaseModel):
    userId: str
    email: EmailStr
    items: list[CartItemRequest] = Field(min_length=1)


class UpdateOrderRequest(BaseModel):
    id: str
    status: Optional[str] = None
    userId: Optional[str] = None
    email: Optional[EmailStr] = None
    items: Optional[list[CartItemRequest]] = None


class UpdateOrderByIdRequest(BaseModel):
    status: Optional[str] = None
    userId: Optional[str] = None
    email: Optional[EmailStr] = None
    items: Optional[list[CartItemRequest]] = None


class DeleteOrderRequest(BaseModel):
    id: str
