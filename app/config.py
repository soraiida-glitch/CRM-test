from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    salesforce_username: str = ""
    salesforce_password: str = ""
    salesforce_security_token: str = ""
    salesforce_domain: str = "login"
    api_secret_token: str = "dev-secret-token"
    log_level: str = "INFO"
    environment: str = "local"
    app_version: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"local", "production"}:
            raise ValueError("ENVIRONMENT must be 'local' or 'production'")
        return normalized

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
