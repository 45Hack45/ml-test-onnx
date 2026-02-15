from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from FastEmbed.QAnswers.models.document import DocumentChunk


class Chat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    query: str
    source_document_id: Optional[int] = Field(
        default=None, foreign_key="documentchunk.id"
    )
    source_document: Optional["DocumentChunk"] = Relationship(back_populates="chats")
    confidence: Optional[float] = 0


class ChatQuery(SQLModel):
    query: str
    k: Optional[int] = 5


class ChatRead(SQLModel):
    id: int
    query: str
    response: str
    source_document_name: Optional[str] = ""
    source_line: Optional[int] = 0
    confidence: Optional[float] = 0
