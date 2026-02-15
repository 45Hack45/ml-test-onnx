from typing import List
import numpy as np
from sqlmodel import Session, select
from fastapi import HTTPException
from FastEmbed.QAnswers.models.document import DocumentChunk
from FastEmbed.QAnswers.models.chat import Chat, ChatQuery, ChatRead
from FastEmbed.core.embedding import get_embedding_engine

embedding_engine = get_embedding_engine()


class ChatService:
    async def query_question(self, query: ChatQuery, session: Session) -> ChatRead:
        """
        Query a question.
        Args:
            query (ChatQuery): The question to query.
            session (Session): Database session.

        Returns:
            ChatRead: The query result.
        """

        chunks_with_embeddings = session.exec(
            select(DocumentChunk).where(DocumentChunk.embedding.is_not(None))
        ).all()

        if len(chunks_with_embeddings) == 0:
            raise HTTPException(
                status_code=404, detail="No documents found in the system"
            )

        # Embed the query
        query_embedding = embedding_engine.embed_query_text(query.query)
        embeddings = [
            embedding_engine.deserialize_embedding(chunk.embedding)
            for chunk in chunks_with_embeddings
        ]

        # Rank and select best chunks
        documents_embeddings = np.stack(embeddings)

        similarity_scores, ranking_indices = (
            embedding_engine.rank_documents_by_similarity(
                query_embedding, documents_embeddings, k=query.k
            )
        )
        selected_chunks = [chunks_with_embeddings[i] for i in ranking_indices]

        # Weighted random selection of chunk based on the similarity scores
        weights = [
            min(chunk.content.count(" "), 10) * (1 + similarity_scores[i])
            for i, chunk in enumerate(selected_chunks)
        ]

        selected_chunk = None
        total = sum(weights)
        random_value = np.random.uniform(0, total)
        for i, (weight, chunk) in enumerate(zip(weights, selected_chunks)):
            random_value -= weight
            if random_value <= 0:
                selected_chunk = chunk
                confidence = similarity_scores[i]
                break

        if not selected_chunk:
            # Should never happen
            raise HTTPException(status_code=500, detail="No source document found")

        # Save and return
        chat = Chat(
            query=query.query,
            source_document=selected_chunk,
            source_line=selected_chunk.line_number,
            confidence=confidence,
        )
        session.add(chat)
        session.commit()
        session.refresh(chat)

        if selected_chunk.document:
            source_document_name = selected_chunk.document.name or "none"
        else:
            source_document_name = "none"

        return ChatRead(
            id=chat.id,
            query=query.query,
            response=selected_chunk.content,
            source_document_name=source_document_name,
            source_line=selected_chunk.line_number,
            confidence=confidence,
        )

    async def get_chat(self, chat_id: int, session: Session) -> ChatRead:
        """
        Get a chat by ID.

        Args:
            chat_id (int): The ID of the chat to get.
            session (Session): The database session.

        Returns:
            ChatRead: The chat.

        Raises:
            HTTPException: If the chat is not found.
        """

        chat = session.get(Chat, chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")

        return ChatRead(
            id=chat.id,
            query=chat.query,
            response=chat.source_document.content,
            source_document_name=chat.source_document.document.name,
            source_line=chat.source_document.line_number,
            confidence=chat.confidence,
        )

    async def get_all_chats(self, session: Session) -> List[ChatRead]:
        """
        Get all chats from the database.

        Args:
            session (Session): The database session.

        Returns:
            List[ChatRead]: A list of all chats.
        """
        chats = session.exec(select(Chat)).all()
        return [
            ChatRead(
                id=chat.id,
                query=chat.query,
                response=chat.source_document.content,
                source_document_name=chat.source_document.document.name,
                source_line=chat.source_document.line_number,
                confidence=chat.confidence,
            )
            for chat in chats
        ]
