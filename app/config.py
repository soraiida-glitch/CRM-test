import os
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from google.cloud import secretmanager
except ImportError:  # pragma: no cover - optional outside production
    secretmanager = None


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
    gcp_project_id: str = ""
    openai_api_key_secret_name: str = "OPENAI_API_KEY"
    salesforce_username_secret_name: str = "SALESFORCE_USERNAME"
    salesforce_password_secret_name: str = "SALESFORCE_PASSWORD"
    salesforce_security_token_secret_name: str = "SALESFORCE_SECURITY_TOKEN"
    api_secret_token_secret_name: str = "API_SECRET_TOKEN"

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


def _access_secret(project_id: str, secret_name: str) -> str:
    if not secretmanager or not project_id or not secret_name:
        return ""
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": secret_path})
    return response.payload.data.decode("utf-8")


def _load_production_overrides() -> dict[str, str]:
    environment = os.getenv("ENVIRONMENT", "local").lower()
    if environment != "production":
        return {}

    project_id = os.getenv("GCP_PROJECT_ID", "")
    if not project_id:
        return {}

    mapping = {
        "openai_api_key": os.getenv("OPENAI_API_KEY_SECRET_NAME", "OPENAI_API_KEY"),
        "salesforce_username": os.getenv(
            "SALESFORCE_USERNAME_SECRET_NAME", "SALESFORCE_USERNAME"
        ),
        "salesforce_password": os.getenv(
            "SALESFORCE_PASSWORD_SECRET_NAME", "SALESFORCE_PASSWORD"
        ),
        "salesforce_security_token": os.getenv(
            "SALESFORCE_SECURITY_TOKEN_SECRET_NAME", "SALESFORCE_SECURITY_TOKEN"
        ),
        "api_secret_token": os.getenv("API_SECRET_TOKEN_SECRET_NAME", "API_SECRET_TOKEN"),
    }

    overrides: dict[str, str] = {"gcp_project_id": project_id}
    for field_name, secret_name in mapping.items():
        if os.getenv(field_name.upper()):
            continue
        secret_value = _access_secret(project_id, secret_name)
        if secret_value:
            overrides[field_name] = secret_value
    return overrides


@lru_cache
def get_settings() -> Settings:
    return Settings(**_load_production_overrides())


settings = get_settings()
