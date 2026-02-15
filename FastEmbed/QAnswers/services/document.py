from typing import List
from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select, delete

import pdfplumber

from FastEmbed.QAnswers.models.document import Document, DocumentChunk
from FastEmbed.core.embedding import get_embedding_engine

embedding_engine = get_embedding_engine()


class DocumentService:
    def upload_document(
        self, file: UploadFile, session: Session, min_length: int = 30
    ) -> Document:
        """
        Upload a document to the system.

        Args:
            file (UploadFile): The document to upload.
            session (Session): The database session.
            min_length (int, optional): The minimum word count of a line,
                smaller lines are combined into a single line. Defaults to 30.

        Returns:
            Document: The uploaded document.
        """
        document_db = Document(name=file.filename or "none")

        content = self.extract_text_from_file(file)

        lines = content.splitlines(keepends=False)

        # Preprocess the lines by combining short lines into a single line
        preprocessed_lines = []
        line_number = 1
        line_buffer = ""
        for line in lines:
            stripped_line = line.strip()
            if (
                len(stripped_line.split()) < min_length
                and len(line_buffer.split()) < min_length
            ):
                line_buffer += stripped_line + " "
            else:
                if line_buffer:
                    preprocessed_lines.append((line_buffer.strip(), line_number))
                    line_buffer = ""
                else:
                    preprocessed_lines.append((stripped_line, line_number))

            line_number += 1

        if line_buffer:
            preprocessed_lines.append((line_buffer.strip(), line_number))

        # Embed and store the lines in the database
        for line_text, line_number in preprocessed_lines:
            if not line_text.strip():
                continue

            document_db.chunks.append(
                DocumentChunk(
                    line_number=line_number,
                    content=line_text,
                    embedding=embedding_engine.serialize_embedding(
                        embedding_engine.embed_document_text(line_text)
                    ),
                )
            )

        session.add(document_db)
        session.commit()
        session.refresh(document_db)

        return document_db

    def extract_text_from_file(self, file: UploadFile) -> str:
        """
        Extracts the text from a file.

        Supported file types: .txt and .pdf

        Args:
            file (UploadFile): The file to extract the text from.

        Returns:
            str: The extracted text.
        """

        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        if not file.filename:
            raise HTTPException(status_code=400, detail="No file name provided")

        if file.filename.endswith(".txt"):
            text = file.file.read().decode("utf-8")

        elif file.filename.endswith(".pdf"):
            with pdfplumber.open(file.file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()

        else:
            raise HTTPException(status_code=400, detail="File format not supported")

        return text

    async def get_documents(self, session: Session) -> List[Document]:
        """
        Get all documents from the system.

        Args:
            session (Session): The database session.

        Returns:
            List[Document]: The list of documents.
        """
        documents = session.scalars(select(Document)).all()
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found")

        return documents

    async def get_document(self, document_id: int, session: Session) -> Document:
        """
        Get a document from the system.

        Args:
            document_id (int): The ID of the document to get.
            session (Session): The database session.

        Returns:
            Document: The document.
        """
        document = session.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return document

    async def delete_document(self, document_id: int, session: Session) -> Document:
        """
        Delete a document from the system.

        Args:
            document_id (int): The ID of the document to delete.
            session (Session): The database session.

        Returns:
            None
        """
        document = session.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        session.delete(document)
        session.commit()

        return document

    async def delete_all_documents(self, session: Session) -> None:
        """
        Delete all documents from the system.

        Args:
            session (Session): The database session.

        Returns:
            None
        """
        session.exec(delete(DocumentChunk))
        session.exec(delete(Document))
        session.commit()
