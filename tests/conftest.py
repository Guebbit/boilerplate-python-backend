import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope='session', autouse=True)
def _env_setup():
    os.environ['MONGO_URI'] = 'mongomock://localhost'
    os.environ['MONGO_DB'] = 'testdb'
    os.environ['ACCESS_TOKEN_SECRET'] = 'test-access-secret'
    os.environ['REFRESH_TOKEN_SECRET'] = 'test-refresh-secret'


@pytest.fixture()
def client():
    from app.core.config import get_settings
    from app.core import database

    get_settings.cache_clear()
    database._db = None
    database._client = None

    from app.main import app

    with TestClient(app) as test_client:
        db = database.get_db()
        db.users.delete_many({})
        db.products.delete_many({})
        db.orders.delete_many({})
        yield test_client
