from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

from app.schemas import ApplicationRecord, ApplicationStatus

DB_PATH = Path("data/applications.db")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT NOT NULL,
                status TEXT NOT NULL,
                error_log TEXT,
                resume_pdf_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def create_application(job_url: str) -> ApplicationRecord:
    now = datetime.now(UTC).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO applications (job_url, status, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (job_url, "Pending", now, now),
        )
        app_id = cur.lastrowid

    return get_application(app_id)


def get_application(app_id: int) -> ApplicationRecord:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()

    if row is None:
        raise ValueError(f"Application id {app_id} not found")

    return _row_to_record(row)


def list_applications(limit: int = 50) -> list[ApplicationRecord]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [_row_to_record(r) for r in rows]


def update_application(
    app_id: int,
    status: ApplicationStatus,
    *,
    error_log: str | None = None,
    resume_pdf_path: str | None = None,
) -> None:
    now = datetime.now(UTC).isoformat()
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE applications
            SET status = ?, error_log = ?, resume_pdf_path = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, error_log, resume_pdf_path, now, app_id),
        )


def _row_to_record(row: sqlite3.Row) -> ApplicationRecord:
    return ApplicationRecord(
        id=row["id"],
        job_url=row["job_url"],
        status=row["status"],
        error_log=row["error_log"],
        resume_pdf_path=row["resume_pdf_path"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )
