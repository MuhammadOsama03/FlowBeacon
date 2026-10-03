import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str = "flowbeacon.db"

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(database_path=os.getenv("FLOWBEACON_DATABASE_PATH", cls.database_path))

