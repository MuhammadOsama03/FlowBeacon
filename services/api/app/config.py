import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str = "flowbeacon.db"
    ingestion_api_key: str | None = None
    environment: str = "development"
    allowed_hosts: tuple[str, ...] = ("localhost", "127.0.0.1", "testserver")

    @classmethod
    def from_environment(cls) -> "Settings":
        settings = cls(
            database_path=os.getenv("FLOWBEACON_DATABASE_PATH", cls.database_path),
            ingestion_api_key=os.getenv("FLOWBEACON_INGESTION_API_KEY") or None,
            environment=os.getenv("FLOWBEACON_ENVIRONMENT", cls.environment).lower(),
            allowed_hosts=tuple(host.strip() for host in
                os.getenv("FLOWBEACON_ALLOWED_HOSTS", ",".join(cls.allowed_hosts)).split(",")
                if host.strip()),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if self.environment not in {"development", "test", "production"}:
            raise ValueError("FLOWBEACON_ENVIRONMENT must be development, test, or production")
        if not self.allowed_hosts:
            raise ValueError("FLOWBEACON_ALLOWED_HOSTS must contain at least one host")
        if self.environment == "production" and (
            self.ingestion_api_key is None or len(self.ingestion_api_key) < 24
        ):
            raise ValueError("production requires an ingestion API key of at least 24 characters")
