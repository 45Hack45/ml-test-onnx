# ml-test-onnx

FastAPI application to retrive information from documents

## Description
This project is a FastAPI application that allows users to upload documents to the system and ask questions about the uploaded documents. The application uses the ONNX Runtime to run the models and a HuggingFace embedding transformer to embed the documents (text and pdf) and later ask questions about the documents.


## Features
- Upload documents to the system
- Ask questions about the uploaded documents

## Installation

### Clone the Repository

```bash
git clone https://github.com/45Hack45/ml-test-onnx.git
cd ml-test-onnx
```

### Initialize SQLite Database
- Rename `.env.example` to `.env` and fill in the required environment variables.

```bash
alembic upgrade head
```

### Build & Run
Note that the first execution will take a while to install requirements/build image and download the model from the HuggingFace Hub.
#### Docker
Build
```bash
docker compose build
```

Run
```bash
docker compose up
```
#### Bare Metal / Local Development
Install requirements
```bash
pip install -r requirements.txt
```

Run
```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

## Usage
The backend service is accessible at http://localhost:8080.

## Documentation

The API documentation is available at http://localhost:8080/docs.

### Endpoints

#### GET /
Healthcheck

#### GET /api/v1/healthcheck
Healthcheck

#### Documents

##### POST /api/v1/documents/upload
Create Document

##### GET /api/v1/documents/
Get Documents

##### GET /api/v1/documents/{document_id}
Get Document

##### DELETE /api/v1/documents/{document_id}
Delete Document

##### DELETE /api/v1/documents/all
Delete All Documents

#### Chat

##### POST /api/v1/chat/ask
Query Question

##### GET /api/v1/chat/{chat_id}
Get Chat

##### GET /api/v1/chat/
Get All Chats

