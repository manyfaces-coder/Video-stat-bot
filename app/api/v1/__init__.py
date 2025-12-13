from fastapi import APIRouter
from .services.creators import router as creators_router

router = APIRouter(
    prefix="/api/v1"
)
router.include_router(creators_router)