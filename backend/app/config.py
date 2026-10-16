from pydantic_settings import BaseSettings, SettingsConfigDict


# No database URL is hard-coded: DATABASE_URL must come from the environment.
#   local run  -> backend/.env            (copy of .env.example, gitignored)
#   tests      -> pytest.ini (SQLite)     (environment variables win over .env)
#   docker     -> docker-compose.yml `environment:` (points at the postgres container)
class Settings(BaseSettings):
    app_name: str = "Petal Shop API"
    database_url: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
