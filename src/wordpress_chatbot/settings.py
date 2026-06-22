from pydantic import Field, HttpUrl, SecretStr, computed_field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)

    embedding_model: str = Field(default="text-embedding-3-small")
    embedding_dimensions: int = Field(default=1536)

    vector_table_name: str = Field(default="case_studies_vector")

    aws_bucket: str
    case_studies_s3_key: str = Field(default="case_studies.csv")

    openai_api_key: SecretStr
    openai_base_url: HttpUrl | None = None
    openai_temperature: float = Field(default=0.6)
    openai_model: str = Field(default="gpt-4o-mini")
    topic_guard_model: str = Field(default="gpt-4o-mini")
    audio_transcription_model: str = Field(default="gpt-4o-mini-transcribe")

    user_id_cookie_name: str = Field(default="X-User-Id")
    user_id_cookie_max_age: int = Field(default=365 * 24 * 3600)
    chainlit_share_threads: bool = Field(
        default=True
    )  # Allow anyone to view threads created by Chainlit. Add authrozation later

    rate_limit_window_hours: int = Field(default=2)
    rate_limit_max_requests: int = Field(default=30)
    rate_limit_max_tokens: int = Field(default=500_000)

    summarization_trigger_messages: int = Field(default=50)
    summarization_keep_messages: int = Field(default=10)

    topic_guard_history_size: int = Field(
        default=2,
        description="Number of recent messages used for topic classification",
    )

    memory_summary_min_messages: int = Field(
        default=4,
        description="Minimum messages in a thread before persisting a dialog summary",
    )
    memory_summary_context_messages: int = Field(
        default=12,
        description="Number of recent messages included when refreshing a dialog summary",
    )
    admin_secret_key: SecretStr
    admin_username: str = Field(default="admin")
    admin_password: SecretStr

    def _postgres_conninfo(self, *, driver: str) -> str:
        return (
            f"{driver}://{self.postgres_user}:{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def database_url(self) -> str:
        return self._postgres_conninfo(driver="postgresql+psycopg_async")

    @computed_field
    @property
    def checkpointer_url(self) -> str:
        return self._postgres_conninfo(driver="postgresql")


settings = AppSettings()  # ty: ignore[missing-argument]
