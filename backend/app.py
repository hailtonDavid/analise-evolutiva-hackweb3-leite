from __future__ import annotations

import os
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

try:
    from .core import analyze_milk_sample, build_evidence, sample_to_dict, simulate_spectral_reading, tamper_check
    from .db import get_evidence_by_hash, get_evidence_by_id, init_db, list_recent, save_evidence
    from .web3_client import register_evidence
except ImportError:  # permite executar com: cd backend && python app.py
    from core import analyze_milk_sample, build_evidence, sample_to_dict, simulate_spectral_reading, tamper_check
    from db import get_evidence_by_hash, get_evidence_by_id, init_db, list_recent, save_evidence
    from web3_client import register_evidence

app = Flask(__name__)
init_db()


@app.get("/")
def index():
    return render_template("index.html", recent=list_recent(8))


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "analise-evolutiva-web3-leite"})


@app.post("/api/samples/simulate")
def api_simulate_sample():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "normal")
    seed = data.get("seed")
    try:
        sample = simulate_spectral_reading(scenario=scenario, seed=seed)
        return jsonify(sample_to_dict(sample))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/evidence")
def api_create_evidence():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    if "spectral_reading" not in data:
        return jsonify({"error": "Payload inválido. Envie uma amostra com spectral_reading."}), 400
    try:
        analysis = analyze_milk_sample(data)
        evidence = build_evidence(data, analysis)
        tx = register_evidence(evidence)
        save_evidence(evidence, tx)
        return jsonify({"evidence": evidence, "web3_registration": tx})
    except Exception as exc:  # pragma: no cover - retorno seguro para demonstração
        return jsonify({"error": str(exc)}), 500


@app.post("/demo/run")
def demo_run_form():
    scenario = request.form.get("scenario", "normal")
    sample = sample_to_dict(simulate_spectral_reading(scenario=scenario, seed=None))
    analysis = analyze_milk_sample(sample)
    evidence = build_evidence(sample, analysis)
    tx = register_evidence(evidence)
    save_evidence(evidence, tx)
    return render_template("evidence.html", evidence=evidence, tx=tx, valid=tamper_check(evidence))


@app.get("/api/evidence/<evidence_id>")
def api_get_evidence(evidence_id: str):
    evidence = get_evidence_by_id(evidence_id)
    if evidence is None:
        return jsonify({"error": "Evidência não encontrada."}), 404
    return jsonify(evidence)


@app.get("/api/verify/<evidence_hash>")
def api_verify(evidence_hash: str):
    evidence = get_evidence_by_hash(evidence_hash)
    if evidence is None:
        return jsonify({"exists": False, "valid": False, "evidence_hash": evidence_hash}), 404
    return jsonify({"exists": True, "valid": tamper_check(evidence), "evidence": evidence})


@app.get("/verify/<evidence_hash>")
def verify_page(evidence_hash: str):
    evidence = get_evidence_by_hash(evidence_hash)
    return render_template("verify.html", evidence=evidence, evidence_hash=evidence_hash, valid=tamper_check(evidence) if evidence else False)


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=os.getenv("APP_ENV") == "development")
