from pydantic import model_validator
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

    @model_validator(mode="after")
    def normalize_database_urls(self) -> "Settings":
        """Ensure async URL uses asyncpg driver and sync URL uses plain postgresql."""
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace(
                "postgres://", "postgresql+asyncpg://", 1
            )
        elif self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        if self.database_url_sync.startswith("postgres://"):
            self.database_url_sync = self.database_url_sync.replace(
                "postgres://", "postgresql://", 1
            )
        return self


settings = Settings()
