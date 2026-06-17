from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    app_name: str = "Task Manager API"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()  # type: ignore
