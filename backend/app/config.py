from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/govdoc"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/govdoc"
    anthropic_api_key: str = ""
    api_key: str = "dev-api-key-change-me"
    upload_dir: str = "/tmp/govdoc-uploads"
    max_file_size_mb: int = 10
    llm_model: str = "claude-sonnet-4-20250514"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
