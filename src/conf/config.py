from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and ``.env``."""

    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    EMAIL_TOKEN_EXPIRATION_SECONDS: int = 86400
    PASSWORD_RESET_TOKEN_EXPIRATION_SECONDS: int = 900
    REDIS_URL: str = "redis://localhost:6379/0"
    USER_CACHE_TTL_SECONDS: int = 900
    APP_BASE_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = "http://localhost:3000"
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


config = Settings()
