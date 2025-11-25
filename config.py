import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "CrisisLens"
    ENV: str = "dev"
    
    # Storage
    REDIS_URL: str = "redis://localhost:6379/0"
    POSTGRES_URL: str = "postgresql://crisis:lens@localhost:5432/crisislens"
    OPENSEARCH_URL: str = "http://localhost:9200"
    QDRANT_URL: str = "http://localhost:6333"
    
    # API Keys (Dummy defaults for now)
    GOOGLE_FACT_CHECK_KEY: str = "dummy_key"
    YOUTUBE_API_KEY: str = "dummy_key"
    REDDIT_CLIENT_ID: str = "dummy_id"
    REDDIT_CLIENT_SECRET: str = "dummy_secret"
    OPENAI_API_KEY: str = "dummy_key"
    
    # Paths
    MODEL_CACHE_DIR: str = "./ml/cache"

    class Config:
        env_file = ".env"

settings = Settings()
