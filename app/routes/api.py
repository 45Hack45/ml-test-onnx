from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["api"])


@router.get("/health")
async def healthcheck():
    return {"status": "ok"}
