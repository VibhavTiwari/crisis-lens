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
    
    # Database settings
    OPENSEARCH_HOST: str = "localhost"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str = "admin"
    
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/crisislen"

    class Config:
        env_file = ".env"

settings = Settings()
