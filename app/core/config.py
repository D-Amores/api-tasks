from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    app_name: str = "Task Manager API"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    openai_api_key: str
    deepseek_api_key: str

    deepseek_model: str = "deepseek-v4-flash"

    langgraph_strict_msgpack: bool = True


settings = Settings()  # type: ignore
