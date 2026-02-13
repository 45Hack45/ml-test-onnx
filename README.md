# ml-test-onnx

This repository contains the code for the ML RAG backend test.

## Description

The ML RAG backend test is a project that demonstrates the implementation of a FastAPI-based backend service for handling document uploads and answering questions based on the uploaded documents. The backend service uses ONNX models for document embedding and question answering.

## Features
- Upload documents to the system
- Ask questions about the uploaded documents

## Installation

### Clone the Repository

```bash
git clone https://github.com/45Hack45/ml-test-onnx.git
cd ml-test-onnx
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Build

```bash
docker compose build
```

## Run

```bash
docker compose up
```

## Usage
The backend service is accessible at http://localhost:8080.
The documentation is available at http://localhost:8080/docs
