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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
