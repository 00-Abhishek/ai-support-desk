from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI Support Desk API"
    database_url: str = "postgresql+psycopg://support:support@localhost:5432/support_desk"
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173"

    # AI is an optional enhancement. With provider="stub" the app runs fully
    # offline and never needs an API key.
    ai_enabled: bool = True
    ai_provider: str = "stub"
    ai_model: str = "stub-heuristic-v1"
    openai_api_key: str = ""

    @property
    def cors_origin_list(self):
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings():
    return Settings()
