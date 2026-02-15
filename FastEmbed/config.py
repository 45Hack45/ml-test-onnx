from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    MODEL_ID: str
    MODEL_DIR: str
    MODEL_PROVIDERS: List[str] = ["CPUExecutionProvider"]
    TOKENIZER_MAX_LENGTH: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
