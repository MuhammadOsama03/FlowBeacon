import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str = "flowbeacon.db"
    ingestion_api_key: str | None = None

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            database_path=os.getenv("FLOWBEACON_DATABASE_PATH", cls.database_path),
            ingestion_api_key=os.getenv("FLOWBEACON_INGESTION_API_KEY") or None,
        )
