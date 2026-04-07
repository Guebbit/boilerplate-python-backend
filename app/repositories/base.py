from bson import ObjectId
from app.core.errors import AppError


def to_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except Exception as exc:  # noqa: BLE001
        raise AppError(422, 'VALIDATION_ERROR', 'Invalid id format') from exc


def normalize_id(document: dict | None) -> dict | None:
    if not document:
        return document
    document['id'] = str(document.pop('_id'))
    return document
