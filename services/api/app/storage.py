import json
import sqlite3
from pathlib import Path

from .models import TraceEvent


class TraceStore:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS trace_events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            connection.execute(
                """CREATE INDEX IF NOT EXISTS trace_events_run_time
                ON trace_events(run_id, timestamp, event_id)"""
            )

    def insert(self, event: TraceEvent) -> bool:
        payload = event.model_dump_json()
        with self._connect() as connection:
            cursor = connection.execute(
                """INSERT OR IGNORE INTO trace_events(event_id, run_id, timestamp, payload)
                VALUES (?, ?, ?, ?)""",
                (event.event_id, event.run_id, event.timestamp.isoformat(), payload),
            )
        return cursor.rowcount == 1

    def get_run(self, run_id: str) -> list[TraceEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT payload FROM trace_events
                WHERE run_id = ? ORDER BY timestamp, event_id""",
                (run_id,),
            ).fetchall()
        return [TraceEvent.model_validate(json.loads(row[0])) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

