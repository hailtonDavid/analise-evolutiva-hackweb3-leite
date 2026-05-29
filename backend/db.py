from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "analise_evolutiva.db"


def _db_path() -> str:
    database_url = os.getenv("DATABASE_URL", "")
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "", 1)
    return str(DEFAULT_DB_PATH)


def get_connection() -> sqlite3.Connection:
    path = Path(_db_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with get_connection() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                evidence_hash TEXT NOT NULL UNIQUE,
                batch_id TEXT NOT NULL,
                producer_id TEXT NOT NULL,
                status TEXT NOT NULL,
                transaction_hash TEXT NOT NULL,
                blockchain_mode TEXT NOT NULL,
                created_at TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        con.commit()


def save_evidence(evidence: Dict[str, Any], tx: Dict[str, Any]) -> None:
    sample = evidence["sample"]
    analysis = evidence["analysis"]
    with get_connection() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO evidence
            (evidence_id, evidence_hash, batch_id, producer_id, status, transaction_hash, blockchain_mode, created_at, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence["evidence_id"],
                evidence["evidence_hash"],
                sample["batch_id"],
                sample["producer_id"],
                analysis["status"],
                tx["transaction_hash"],
                tx["mode"],
                evidence["created_at"],
                json.dumps(evidence, ensure_ascii=False),
            ),
        )
        con.commit()


def get_evidence_by_id(evidence_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as con:
        row = con.execute("SELECT * FROM evidence WHERE evidence_id = ?", (evidence_id,)).fetchone()
        if row is None:
            return None
        payload = json.loads(row["payload"])
        payload["transaction_hash"] = row["transaction_hash"]
        payload["blockchain_mode"] = row["blockchain_mode"]
        return payload


def get_evidence_by_hash(evidence_hash: str) -> Optional[Dict[str, Any]]:
    with get_connection() as con:
        row = con.execute("SELECT * FROM evidence WHERE evidence_hash = ?", (evidence_hash,)).fetchone()
        if row is None:
            return None
        payload = json.loads(row["payload"])
        payload["transaction_hash"] = row["transaction_hash"]
        payload["blockchain_mode"] = row["blockchain_mode"]
        return payload


def list_recent(limit: int = 10) -> list[Dict[str, Any]]:
    with get_connection() as con:
        rows = con.execute(
            "SELECT evidence_id, evidence_hash, batch_id, producer_id, status, transaction_hash, blockchain_mode, created_at FROM evidence ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
