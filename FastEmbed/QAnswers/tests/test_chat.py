# tests/test_chat_service.py
import pytest
from unittest.mock import MagicMock
from sqlmodel import Session
from fastapi import HTTPException, UploadFile

from FastEmbed.QAnswers.services.chat import ChatService, ChatQuery
from FastEmbed.QAnswers.models.chat import Chat, ChatRead
from FastEmbed.QAnswers.models.document import DocumentChunk, Document


@pytest.mark.asyncio
async def test_get_chat_success():
    # Init
    chat_id = 1

    content = "Hello world"
    mock_chunk = DocumentChunk(
        line_number=5,
        content=content,
        embedding=content.encode("utf-8"),
    )
    Document(name="TestDoc", chunks=[mock_chunk])

    mock_chat = Chat(
        id=chat_id,
        query="Test query",
        source_document=mock_chunk,
        confidence=0.9,
    )

    mock_session = MagicMock(spec=Session)
    mock_session.get.return_value = mock_chat

    service = ChatService()

    # Test
    result = await service.get_chat(chat_id, mock_session)

    # Assert
    assert isinstance(result, ChatRead)
    assert result.id == chat_id
    assert result.query == mock_chat.query
    assert result.response == content
    assert result.source_document_name == mock_chunk.document.name
    assert result.source_line == mock_chunk.line_number
    assert result.confidence == mock_chat.confidence


@pytest.mark.asyncio
async def test_get_chat_not_found():
    # Init
    chat_id = 1
    mock_session = MagicMock(spec=Session)
    mock_session.get.return_value = None

    service = ChatService()

    # Test
    with pytest.raises(HTTPException) as exc_info:
        await service.get_chat(chat_id, mock_session)

    # Assert
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Chat not found"


@pytest.mark.asyncio
async def test_get_all_chats():
    # Init
    mock_chunk1 = DocumentChunk(
        line_number=5,
        content="Hello world",
        embedding="Hello world".encode("utf-8"),
    )

    mock_chunk2 = DocumentChunk(
        line_number=10,
        content="Another chunk",
        embedding="Another chunk".encode("utf-8"),
    )
    mock_document = Document(name="TestDoc", chunks=[mock_chunk1, mock_chunk2])

    chat1 = Chat(id=1, query="Query 1", source_document=mock_chunk1, confidence=0.8)
    chat2 = Chat(id=2, query="Query 2", source_document=mock_chunk2, confidence=0.95)

    mock_session = MagicMock(spec=Session)
    mock_exec = mock_session.exec.return_value
    mock_exec.all.return_value = [chat1, chat2]

    service = ChatService()

    # Test
    results = await service.get_all_chats(mock_session)

    # Assert
    assert len(results) == 2
    assert results[0].id == 1
    assert results[0].response == "Hello world"
    assert results[1].id == 2
    assert results[1].response == "Another chunk"


@pytest.mark.asyncio
async def test_get_all_chats_empty():
    # Init
    mock_session = MagicMock(spec=Session)
    mock_exec = mock_session.exec.return_value
    mock_exec.all.return_value = []

    service = ChatService()

    # Test
    results = await service.get_all_chats(mock_session)

    # Assert
    assert len(results) == 0


@pytest.mark.asyncio
async def test_query_question():
    # Init
    def fake_add(obj):
        obj.id = 1

    mock_query = ChatQuery(query="Which planet is known as the Red Planet?", k=1)
    mock_mars_chunk = DocumentChunk(
        line_number=74,
        content="Mars, known for its reddish appearance, is often referred to as the Red Planet.",
        embedding=open(
            "FastEmbed/QAnswers/tests/data/mars_chunk_embedding.bin", "rb"
        ).read(),
    )

    mock_document = Document(name="Mars Facts", chunks=[mock_mars_chunk])

    mock_session = MagicMock(spec=Session)
    mock_session.add.side_effect = fake_add
    mock_session.exec.return_value.all.return_value = [
        mock_mars_chunk,
        DocumentChunk(
            line_number=31,
            content="Venus is often called Earth's twin because of its similar size and proximity.",
            embedding=open(
                "FastEmbed/QAnswers/tests/data/venus_chunk_embedding.bin", "rb"
            ).read(),
        ),
        DocumentChunk(
            line_number=100,
            content="Jupiter, the largest planet in our solar system, has a prominent red spot.",
            embedding=open(
                "FastEmbed/QAnswers/tests/data/jupiter_chunk_embedding.bin", "rb"
            ).read(),
        ),
    ]

    service = ChatService()

    # Test
    result = await service.query_question(mock_query, mock_session)

    # Assert
    assert isinstance(result, ChatRead)
    assert result.query == mock_query.query
    assert result.response == mock_mars_chunk.content
    assert result.source_document_name == mock_mars_chunk.document.name
    assert result.source_line == mock_mars_chunk.line_number


@pytest.mark.asyncio
async def test_query_question_no_documents():
    # Init
    mock_query = ChatQuery(query="Which planet is known as the Red Planet?")
    mock_session = MagicMock(spec=Session)

    service = ChatService()

    # Test
    with pytest.raises(HTTPException) as exc_info:
        await service.query_question(mock_query, mock_session)

    # Assert
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No documents found in the system"
