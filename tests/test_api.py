from bson import ObjectId

from app.core.database import get_db
from app.core.security import hash_password


def create_user(email: str, username: str, password: str, admin: bool = False):
    db = get_db()
    user_id = db.users.insert_one(
        {
            'email': email,
            'username': username,
            'passwordHash': hash_password(password),
            'admin': admin,
            'active': True,
            'cart': [],
            'tokens': [],
            'deletedAt': None,
        }
    ).inserted_id
    return str(user_id)


def create_product(title: str, price: float, active: bool = True):
    db = get_db()
    product_id = db.products.insert_one(
        {
            'title': title,
            'price': price,
            'active': active,
            'description': None,
            'deletedAt': None,
        }
    ).inserted_id
    return str(product_id)


def login_and_get_token(client, email: str, password: str) -> str:
    response = client.post('/account/login', json={'email': email, 'password': password})
    assert response.status_code == 200
    payload = response.json()
    assert payload['success'] is True
    return payload['data']['token']


def auth_headers(token: str) -> dict:
    return {'Authorization': f'Bearer {token}'}


def test_login_and_get_account(client):
    create_user('user@example.com', 'user', 'password123')
    token = login_and_get_token(client, 'user@example.com', 'password123')

    account_response = client.get('/account', headers=auth_headers(token))
    assert account_response.status_code == 200
    account_data = account_response.json()['data']
    assert account_data['email'] == 'user@example.com'


def test_users_endpoint_requires_admin(client):
    create_user('user@example.com', 'user', 'password123', admin=False)
    token = login_and_get_token(client, 'user@example.com', 'password123')

    response = client.get('/users', headers=auth_headers(token))
    assert response.status_code == 403


def test_products_public_vs_admin_visibility(client):
    create_user('admin@example.com', 'admin', 'password123', admin=True)
    create_product('Active Product', 10.0, active=True)
    create_product('Hidden Product', 25.0, active=False)

    public_response = client.get('/products')
    assert public_response.status_code == 200
    public_items = public_response.json()['data']['items']
    assert len(public_items) == 1
    assert public_items[0]['title'] == 'Active Product'

    admin_token = login_and_get_token(client, 'admin@example.com', 'password123')
    admin_response = client.get('/products', headers=auth_headers(admin_token))
    assert admin_response.status_code == 200
    admin_items = admin_response.json()['data']['items']
    assert len(admin_items) == 2


def test_checkout_creates_order_and_clears_cart(client):
    create_user('user@example.com', 'user', 'password123', admin=False)
    product_id = create_product('Book', 12.5, active=True)
    token = login_and_get_token(client, 'user@example.com', 'password123')

    add_item = client.post('/cart', headers=auth_headers(token), json={'productId': product_id, 'quantity': 2})
    assert add_item.status_code == 200

    checkout = client.post('/cart/checkout', headers=auth_headers(token), json={})
    assert checkout.status_code == 201
    order = checkout.json()['data']['order']
    assert order['total'] == 25.0

    cart_after = client.get('/cart', headers=auth_headers(token))
    assert cart_after.status_code == 200
    assert cart_after.json()['data']['summary']['itemsCount'] == 0


def test_order_scoping_non_admin(client):
    user1 = create_user('u1@example.com', 'u1', 'password123', admin=False)
    user2 = create_user('u2@example.com', 'u2', 'password123', admin=False)
    create_user('admin@example.com', 'admin', 'password123', admin=True)
    product_id = create_product('Mouse', 50.0, active=True)

    db = get_db()
    db.orders.insert_many(
        [
            {
                '_id': ObjectId(),
                'userId': user1,
                'email': 'u1@example.com',
                'items': [{'productId': product_id, 'title': 'Mouse', 'price': 50.0, 'quantity': 1}],
                'total': 50.0,
                'status': 'pending',
            },
            {
                '_id': ObjectId(),
                'userId': user2,
                'email': 'u2@example.com',
                'items': [{'productId': product_id, 'title': 'Mouse', 'price': 50.0, 'quantity': 1}],
                'total': 50.0,
                'status': 'pending',
            },
        ]
    )

    user1_token = login_and_get_token(client, 'u1@example.com', 'password123')
    user1_orders = client.get('/orders', headers=auth_headers(user1_token))
    assert user1_orders.status_code == 200
    assert len(user1_orders.json()['data']['items']) == 1

    admin_token = login_and_get_token(client, 'admin@example.com', 'password123')
    admin_orders = client.get('/orders', headers=auth_headers(admin_token))
    assert admin_orders.status_code == 200
    assert len(admin_orders.json()['data']['items']) == 2
