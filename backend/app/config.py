from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Petal Shop API"
    database_url: str = "postgresql+psycopg://petal:petal@localhost:5432/petal"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
