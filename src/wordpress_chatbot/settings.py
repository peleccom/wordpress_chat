from pydantic import Field, HttpUrl, SecretStr, computed_field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    pass


settings = AppSettings()  # ty: ignore[missing-argument]
