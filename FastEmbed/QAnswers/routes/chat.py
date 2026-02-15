from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from FastEmbed.core.database import get_session
from FastEmbed.QAnswers.models.chat import Chat, ChatQuery, ChatRead
from FastEmbed.QAnswers.services.chat import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()


@router.post("/ask", response_model=ChatRead)
async def query_question(
    chat_query: ChatQuery, session: Session = Depends(get_session)
) -> ChatRead:
    """
    Query information from the system documents.
    If k is 1 it will return the best match else
    it will return a random one of the best k matches
    """
    return await chat_service.query_question(chat_query, session)


@router.get("/{chat_id}", response_model=ChatRead)
async def get_chat(chat_id: int, session: Session = Depends(get_session)) -> ChatRead:
    """
    Get a chat by ID.
    """
    return await chat_service.get_chat(chat_id, session)


@router.get("/", response_model=List[ChatRead])
async def get_all_chats(session: Session = Depends(get_session)) -> List[ChatRead]:
    """
    Get all chats.
    """
    return await chat_service.get_all_chats(session)
