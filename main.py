from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from FastEmbed.QAnswers.routes.api import router as api_router
from FastEmbed.core.database import init_database
from FastEmbed.core.embedding import init_embedding_engine

from contextlib import asynccontextmanager


@asynccontextmanager
async def application_lifecycle(app: FastAPI):

    # Initialize embedding engine
    init_embedding_engine()

    yield

    # Clean up after application shutdown


app = FastAPI(lifespan=application_lifecycle)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Server is running"}


app.include_router(api_router)
