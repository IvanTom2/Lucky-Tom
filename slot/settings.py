from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    GRPC_PORT: int = 50051

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str

    CACHE_HOST: str
    CACHE_PORT: int
    CACHE_USER: str
    CACHE_PASS: SecretStr
    CACHE_NAME: str

    QUEUE_HOST: str
    QUEUE_PORT: int
    QUEUE_USER: str
    QUEUE_PASS: SecretStr
    VERSION_QUEUE: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def DB_DSN(self) -> str:
        return (
            f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS.get_secret_value()}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )

    @property
    def CACHE_DSN(self) -> str:
        return (
            f"redis://{settings.CACHE_USER}:{settings.CACHE_PASS.get_secret_value()}"
            f"@{settings.CACHE_HOST}:{settings.CACHE_PORT}/{settings.CACHE_NAME}"
        )

    @property
    def QUEUE_DSN(self) -> str:
        return (
            f"amqp://{settings.QUEUE_USER}:{settings.QUEUE_PASS.get_secret_value()}"
            f"@{settings.QUEUE_HOST}:{settings.QUEUE_PORT}"
        )


settings = Settings()  # type:ignore
