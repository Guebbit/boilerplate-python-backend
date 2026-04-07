from fastapi import APIRouter
from app.core.responses import success_response

router = APIRouter(tags=['system'])


@router.get('/health')
def health():
    return success_response(200, 'SYSTEM_HEALTHY', {'status': 'ok'})
