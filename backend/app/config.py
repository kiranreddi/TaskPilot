from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./taskpilot.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    STRIPE_WEBHOOK_SECRET: str = "whsec_test"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
