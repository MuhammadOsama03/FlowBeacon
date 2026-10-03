from functools import lru_cache

from .config import Settings
from .ingestion import TraceIngestor
from .storage import TraceStore


@lru_cache(maxsize=1)
def get_store() -> TraceStore:
    return TraceStore(Settings.from_environment().database_path)


def get_ingestor() -> TraceIngestor:
    return TraceIngestor(get_store())


def reset_dependencies() -> None:
    get_store.cache_clear()

