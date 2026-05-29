from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

from core import create_sample, verify_integrity

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "analise_evolutiva_mvp.sqlite3"

app = Flask(__name__)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id TEXT NOT NULL,
                lot_id TEXT NOT NULL,
                evidence_hash TEXT NOT NULL UNIQUE,
                classification TEXT NOT NULL,
                tx_hash TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_sample(sample: Dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO samples
            (sample_id, lot_id, evidence_hash, classification, tx_hash, payload_json, created_at_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sample["sample_id"],
                sample["lot_id"],
                sample["evidence_hash"],
                sample["analysis"]["classificacao"],
                sample["blockchain"]["tx_hash"],
                json.dumps(sample, ensure_ascii=False),
                sample["created_at_utc"],
            ),
        )
        conn.commit()


def list_samples(limit: int = 25) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, sample_id, lot_id, evidence_hash, classification, tx_hash, created_at_utc FROM samples ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_sample_by_hash(evidence_hash: str) -> Dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT payload_json FROM samples WHERE evidence_hash = ?", (evidence_hash,)).fetchone()
    if row is None:
        return None
    return json.loads(row["payload_json"])


@app.route("/")
def index():
    samples = list_samples()
    return render_template("index.html", samples=samples)


@app.route("/api/amostras", methods=["GET"])
def api_list_samples():
    return jsonify({"items": list_samples()})


@app.route("/api/amostras/simular", methods=["POST"])
def api_simulate_sample():
    data = request.get_json(silent=True) or {}
    seed = data.get("seed")
    adulterated = data.get("adulterated")
    sample = create_sample(
        seed=seed,
        producer_name=data.get("producer_name", "Produtor demonstrativo"),
        farm_name=data.get("farm_name", "Fazenda Piloto"),
        city=data.get("city", "Goiás"),
        adulterated=adulterated,
    )
    insert_sample(sample)
    return jsonify(sample), 201


@app.route("/api/verificar/<evidence_hash>", methods=["GET"])
def api_verify(evidence_hash: str):
    sample = get_sample_by_hash(evidence_hash)
    if not sample:
        return jsonify({"encontrado": False, "mensagem": "Evidencia nao encontrada."}), 404
    integrity = verify_integrity(sample)
    return jsonify({"encontrado": True, "integridade": integrity, "amostra": sample})


@app.route("/verificar/<evidence_hash>", methods=["GET"])
def verify_page(evidence_hash: str):
    sample = get_sample_by_hash(evidence_hash)
    if not sample:
        return render_template("verify.html", found=False, evidence_hash=evidence_hash, sample=None, integrity=None), 404
    integrity = verify_integrity(sample)
    return render_template("verify.html", found=True, evidence_hash=evidence_hash, sample=sample, integrity=integrity)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "project": "Analise Evolutiva HackWeb 3.0 MVP"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
