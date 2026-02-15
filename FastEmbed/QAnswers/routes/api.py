from fastapi import APIRouter
from FastEmbed.QAnswers.routes.document import router as document_router
from FastEmbed.QAnswers.routes.chat import router as chat_router

router = APIRouter(prefix="/api/v1", tags=["api"])

router.include_router(document_router)
router.include_router(chat_router)


@router.get("/healthcheck")
async def get_healthcheck():
    """
    Healthcheck endpoint.
    """
    return {"status": "ok"}
