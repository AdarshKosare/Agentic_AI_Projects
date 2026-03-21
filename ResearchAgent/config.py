from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    google_api_key: str = Field(default="")
    primary_model: str = Field(default="gemini-2.0-flash")
    fallback_model: str = Field(default="llama3.1:8b")
    temperature: float = Field(default=0.1)
    max_tokens: int = Field(default=8192)

    # Search
    tavily_api_key: str = Field(default="")
    max_search_results: int = Field(default=5)

    # Agent
    max_iterations: int = Field(default=10)

    @property
    def has_gemini(self) -> bool:
        return bool(self.google_api_key)

    @property
    def has_tavily(self) -> bool:
        return bool(self.tavily_api_key)
<<<<<<< HEAD
=======
    
    # RAG
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    chroma_persist_dir: str = Field(default="./chroma_db")
    chunk_size: int = Field(default=512)
    chunk_overlap: int = Field(default=64)
>>>>>>> d1fcc8d (RAG + Memory Integration)


settings = Settings()