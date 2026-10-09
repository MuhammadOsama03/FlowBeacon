import json
import sqlite3
from datetime import datetime
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

    def list_run_ids(
        self, *, status: str | None = None, search: str | None = None,
        limit: int = 20, offset: int = 0
    ) -> tuple[list[str], int]:
        clauses, parameters = [], []
        if search:
            clauses.append("run_id LIKE ? ESCAPE '\\'")
            escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            parameters.append(f"%{escaped}%")
        if status:
            clauses.append("json_extract(payload, '$.status') = ?")
            parameters.append(status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            total = connection.execute(
                f"SELECT COUNT(DISTINCT run_id) FROM trace_events {where}", parameters
            ).fetchone()[0]
            rows = connection.execute(
                f"""SELECT run_id, MAX(timestamp) AS latest FROM trace_events {where}
                GROUP BY run_id ORDER BY latest DESC, run_id LIMIT ? OFFSET ?""",
                [*parameters, limit, offset],
            ).fetchall()
        return [row[0] for row in rows], total

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def ping(self) -> bool:
        try:
            with self._connect() as connection:
                return connection.execute("SELECT 1").fetchone() == (1,)
        except sqlite3.Error:
            return False

    def delete_runs_before(self, cutoff: datetime) -> tuple[int, int]:
        """Delete complete runs whose newest event predates the cutoff."""
        cutoff_value = cutoff.isoformat()
        with self._connect() as connection:
            run_ids = [row[0] for row in connection.execute(
                """SELECT run_id FROM trace_events GROUP BY run_id
                HAVING MAX(timestamp) < ?""", (cutoff_value,)).fetchall()]
            if not run_ids:
                return 0, 0
            placeholders = ",".join("?" for _ in run_ids)
            cursor = connection.execute(
                f"DELETE FROM trace_events WHERE run_id IN ({placeholders})", run_ids)
        return len(run_ids), cursor.rowcount
