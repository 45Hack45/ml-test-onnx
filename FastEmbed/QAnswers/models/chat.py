from typing import Annotated, Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from FastEmbed.QAnswers.models.document import DocumentChunk


class Chat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True)
    query: Annotated[str, Field(description="Question to answer")]
    source_document_id: Optional[int] = Field(
        default=None, foreign_key="documentchunk.id", description="Source document"
    )
    source_document: Optional["DocumentChunk"] = Relationship(back_populates="chats")
    confidence: Optional[float] = Field(default=0, description="Confidence score 0-1")


class ChatQuery(SQLModel):
    query: Annotated[str, Field(description="Question to be answered")]
    k: int = Field(
        default=5, description="Number of documents to select with highest ranking"
    )


class ChatRead(SQLModel):
    id: int
    query: str
    response: str
    source_document_name: str = ""
    source_line: int = 0
    confidence: float = 0
