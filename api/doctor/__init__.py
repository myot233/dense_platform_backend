from fastapi import APIRouter
from .info import router as info_router
router = APIRouter()
router.include_router(info_router)
