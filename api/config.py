from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8000
    allowed_origins: list[str] = [
        "https://game.jswindell.dev",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "null",  # local file:// origin
    ]

    mongo_uri: str = ""
    mongo_db: str = "dungeon_crawler"
    mongo_vector_index: str = "game_context_vector_index"

    enable_llm_context: bool = False
    enable_vector_search: bool = False
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 768
    google_cloud_project: str = ""
    google_cloud_location: str = "global"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
