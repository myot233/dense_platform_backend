from fastapi import APIRouter

router = APIRouter()


@router.get("/api/doctors")
async def doctors():
    pass


