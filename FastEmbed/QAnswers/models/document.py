from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from FastEmbed.QAnswers.models.chat import Chat


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    chunks: list["DocumentChunk"] = Relationship(
        back_populates="document", cascade_delete=True
    )


class DocumentChunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(default=None, foreign_key="document.id")
    document: list[Document] = Relationship(back_populates="chunks")
    line_number: int

    content: str
    embedding: bytes = Field()

    chats: list["Chat"] = Relationship(back_populates="source_document")


class DocumentCreate(SQLModel):
    name: str


class DocumentRead(SQLModel):
    id: int
    name: str
