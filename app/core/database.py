from pymongo import MongoClient
from app.core.config import get_settings


_client = None
_db = None


def get_db():
    global _client, _db
    if _db is not None:
        return _db

    settings = get_settings()
    uri = settings.mongo_uri

    if uri.startswith('mongomock://'):
        import mongomock

        _client = mongomock.MongoClient()
    else:
        _client = MongoClient(uri)

    _db = _client[settings.mongo_db]
    return _db
