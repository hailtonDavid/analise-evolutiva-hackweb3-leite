from __future__ import annotations

import os
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

try:
    from .core import analyze_milk_sample, build_chain_evidence, build_evidence, build_full_chain_process, build_complete_ecosystem_evidence, build_complete_evolutionary_analysis, build_complete_ecosystem_evidence, build_complete_evolutionary_analysis, build_investor_impact_model, build_milk_chain_use_cases, sample_to_dict, simulate_spectral_reading, tamper_check
    from .db import get_evidence_by_hash, get_evidence_by_id, init_db, list_recent, save_evidence
    from .web3_client import register_evidence
except ImportError:  # permite executar com: cd backend && python app.py
    from core import analyze_milk_sample, build_chain_evidence, build_evidence, build_full_chain_process, build_complete_ecosystem_evidence, build_complete_evolutionary_analysis, build_complete_ecosystem_evidence, build_complete_evolutionary_analysis, build_investor_impact_model, build_milk_chain_use_cases, sample_to_dict, simulate_spectral_reading, tamper_check
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


@app.get("/simulador")
def simulator_page():
    return render_template("simulator.html")




@app.get("/investidor")
def investor_page():
    return render_template("investor.html")


@app.get("/ecossistema")
def ecosystem_page():
    return render_template("ecosystem.html")




@app.get("/casos-leite")
def milk_use_cases_page():
    return render_template("milk_use_cases.html")


@app.get("/api/use-cases/milk")
def api_milk_use_cases():
    return jsonify(build_milk_chain_use_cases())


@app.get("/site")
def official_site_page():
    return render_template(
        "site.html",
        site_url="https://www.analise-evolutiva.ia.br/",
    )


@app.get("/api/site/meta")
def api_site_meta():
    return jsonify({
        "name": "Análise Evolutiva",
        "official_site": "https://www.analise-evolutiva.ia.br/",
        "integration_mode": "embedded_webview_with_external_fallback",
        "purpose": "Disponibilizar o site institucional dentro do MVP HackWeb 3.0 e manter acesso direto à presença pública da Análise Evolutiva.",
    })


@app.post("/api/ecosystem/simulation")
def api_ecosystem_simulation():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    try:
        ecosystem = build_complete_evolutionary_analysis(
            scenario=data.get("scenario", "normal"),
            seed=data.get("seed", 42),
        )
        return jsonify(ecosystem)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": str(exc)}), 500


@app.post("/api/ecosystem/evidence")
def api_ecosystem_evidence():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    try:
        ecosystem = build_complete_evolutionary_analysis(
            scenario=data.get("scenario", "normal"),
            seed=data.get("seed", 42),
        )
        evidence = build_complete_ecosystem_evidence(ecosystem)
        tx = register_evidence(evidence)
        save_evidence(evidence, tx)
        return jsonify({"ecosystem": ecosystem, "evidence": evidence, "web3_registration": tx})
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": str(exc)}), 500


@app.post("/api/investor/impact")
def api_investor_impact():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    try:
        impact = build_investor_impact_model(
            scenario=data.get("scenario", "normal"),
            seed=data.get("seed", 42),
            monthly_liters=float(data.get("monthly_liters", 450000)),
            milk_price_brl=float(data.get("milk_price_brl", 2.40)),
            baseline_loss_pct=float(data.get("baseline_loss_pct", 0.018)),
            loss_reduction_pct=float(data.get("loss_reduction_pct", 0.42)),
            quality_bonus_pct=float(data.get("quality_bonus_pct", 0.012)),
            audits_per_month=int(data.get("audits_per_month", 24)),
            audit_cost_brl=float(data.get("audit_cost_brl", 180)),
            audit_efficiency_gain_pct=float(data.get("audit_efficiency_gain_pct", 0.45)),
            hardware_kit_brl=float(data.get("hardware_kit_brl", 18500)),
            onboarding_brl=float(data.get("onboarding_brl", 7500)),
            monthly_saas_brl=float(data.get("monthly_saas_brl", 1490)),
            analysis_fee_brl=float(data.get("analysis_fee_brl", 0.35)),
            analyses_per_month=int(data.get("analyses_per_month", 900)),
        )
        return jsonify(impact)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": str(exc)}), 500


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




@app.post("/api/simulator/full-process")
def api_full_process_simulation():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "normal")
    seed = data.get("seed")
    try:
        process = build_full_chain_process(scenario=scenario, seed=seed)
        return jsonify(process)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400



@app.post("/api/spectrometer/session")
def api_spectrometer_session():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "normal")
    seed = data.get("seed")
    try:
        process = build_full_chain_process(scenario=scenario, seed=seed)
        return jsonify(process["spectrophotometer_session"])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400



@app.post("/api/spectrometer/live-sequence")
def api_spectrometer_live_sequence():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "normal")
    seed = data.get("seed")
    try:
        process = build_full_chain_process(scenario=scenario, seed=seed)
        return jsonify({
            "session_id": process["spectrophotometer_session"]["session_id"],
            "scenario": scenario,
            "live_sequence": process["spectrophotometer_session"].get("live_sequence", []),
        })
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/evidence/full-process")
def api_create_full_process_evidence():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    try:
        if "milk_sample" in data and "integrated_analysis" in data:
            process = data
        else:
            process = build_full_chain_process(scenario=data.get("scenario", "normal"), seed=data.get("seed"))
        evidence = build_chain_evidence(process)
        tx = register_evidence(evidence)
        save_evidence(evidence, tx)
        return jsonify({"process": process, "evidence": evidence, "web3_registration": tx})
    except Exception as exc:  # pragma: no cover - retorno seguro para demonstração
        return jsonify({"error": str(exc)}), 500

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
