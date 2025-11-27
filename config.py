import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "CrisisLens"
    ENV: str = "dev"
    
    # Storage
    REDIS_URL: str = "redis://localhost:6379/0"
    
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
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-use-openssl-rand-hex-32"
    
    # OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # ML & Media APIs
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    TINEYE_API_KEY: str = ""
    GOOGLE_SEARCH_API_KEY: str = ""
    GOOGLE_CSE_ID: str = ""
    
    # Model Cache
    MODEL_CACHE_DIR: str = "/app/models/cache"
    MEDIA_ROOT: str = "/app/media"

    class Config:
        env_file = ".env"

settings = Settings()
