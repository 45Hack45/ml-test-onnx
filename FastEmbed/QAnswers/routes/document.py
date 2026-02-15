from fastapi import APIRouter, Depends

from FastEmbed.core.database import get_session
from FastEmbed.QAnswers.models.document import Document, DocumentRead
from FastEmbed.QAnswers.services.document import DocumentService
from sqlmodel import Session
from typing import List
from fastapi import UploadFile

router = APIRouter(prefix="/documents", tags=["documents"])
document_service = DocumentService()


@router.post("/upload", response_model=DocumentRead)
def create_document(
    file: UploadFile,
    min_word_count: int = 30,
    session: Session = Depends(get_session),
) -> Document:
    """
    Create a new document.
    """
    return document_service.upload_document(file, session, min_length=min_word_count)


@router.get("/", response_model=List[DocumentRead])
async def get_documents(session: Session = Depends(get_session)) -> List[Document]:
    """
    Get all documents.
    """
    return await document_service.get_documents(session)


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: int, session: Session = Depends(get_session)
) -> Document:
    """
    Get a document by ID.
    """
    return await document_service.get_document(document_id, session)


@router.delete("/all")
async def delete_all_documents(session: Session = Depends(get_session)):
    """
    Delete all documents.
    """
    await document_service.delete_all_documents(session)

    return {"message": "All documents deleted"}


@router.delete("/{document_id}", response_model=DocumentRead)
async def delete_document(
    document_id: int, session: Session = Depends(get_session)
) -> Document:
    """
    Delete a document by ID.
    """
    return await document_service.delete_document(document_id, session)
