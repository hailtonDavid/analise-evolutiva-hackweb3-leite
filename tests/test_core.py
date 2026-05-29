from backend.core import (
    analyze_milk_sample,
    build_demo_evidence,
    build_full_chain_process,
    build_chain_evidence,
    sample_to_dict,
    simulate_spectral_reading,
    tamper_check,
)


def test_normal_sample_is_valid_evidence():
    sample = sample_to_dict(simulate_spectral_reading("normal", seed=7))
    analysis = analyze_milk_sample(sample)
    evidence = build_demo_evidence("normal", seed=7)

    assert analysis.status in {"APROVADO", "ATENÇÃO", "REPROVADO"}
    assert len(evidence["evidence_hash"]) == 64
    assert tamper_check(evidence) is True


def test_temperature_break_increases_risk():
    normal = sample_to_dict(simulate_spectral_reading("normal", seed=10))
    broken = sample_to_dict(simulate_spectral_reading("temperature_break", seed=10))

    normal_analysis = analyze_milk_sample(normal)
    broken_analysis = analyze_milk_sample(broken)

    assert broken_analysis.temperature_risk > normal_analysis.temperature_risk
    assert broken_analysis.compliance_score < normal_analysis.compliance_score


def test_tampered_evidence_fails_integrity_check():
    evidence = build_demo_evidence("normal", seed=20)
    evidence["analysis"]["status"] = "APROVADO_MANUALMENTE"

    assert tamper_check(evidence) is False


def test_full_chain_process_contains_realistic_matrices():
    process = build_full_chain_process("integrated_risk", seed=42)

    assert process["milk_sample"]["spectrometer_capture"]["channels"]
    assert process["soil"]["capture"]["channels"]
    assert process["feed"]["capture"]["channels"]
    assert process["water"]["capture"]["channels"]
    assert process["integrated_analysis"]["status"] in {"APROVADO", "ATENÇÃO", "REPROVADO"}
    assert len(process["chain_steps"]) >= 8


def test_chain_evidence_hash_is_valid():
    process = build_full_chain_process("normal", seed=5)
    evidence = build_chain_evidence(process)

    assert len(evidence["evidence_hash"]) == 64
    assert evidence["chain_process"]["soil"]["analysis"]
    assert tamper_check(evidence) is True


def test_spectrophotometer_session_contains_qc_and_workflow():
    process = build_full_chain_process("normal", seed=15)
    session = process["spectrophotometer_session"]

    assert session["overall_qc"]["status"] in {"APTO PARA ANÁLISE", "REVISAR LEITURA"}
    assert len(session["workflow"]) >= 8
    assert all(cycle["quality_control"]["mean_snr_db"] > 0 for cycle in session["sample_cycles"])
    assert all(cycle["led_sweep"] for cycle in session["sample_cycles"])


def test_live_spectrometer_sequence_simulates_led_activation():
    process = build_full_chain_process("normal", seed=21)
    sequence = process["spectrophotometer_session"]["live_sequence"]

    assert sequence
    assert any(event["phase"] == "DARK_CAPTURE" and event["led_state"] == "OFF" for event in sequence)
    assert any(event["phase"] == "CHANNEL_CAPTURE" and event["led_state"] == "ON" and event["wavelength_nm"] == 365 for event in sequence)
    assert any(event["phase"] == "CHANNEL_CAPTURE" and event["led_bank"] == "NIR" and event["wavelength_nm"] == 910 for event in sequence)
    assert sequence[-1]["phase"] == "WEB3_REGISTER"


def test_investor_impact_model():
    from backend.core import build_investor_impact_model
    impact = build_investor_impact_model(scenario="normal", seed=42, monthly_liters=120000)
    assert impact["client_value_simulation"]["monthly_liters"] == 120000
    assert impact["business_model_simulation"]["vendor_mrr_brl_per_client"] > 0
    assert len(impact["investment_thesis"]["defensibility"]) >= 3


def test_complete_ecosystem_simulation():
    from backend.core import build_complete_ecosystem_evidence, build_complete_evolutionary_analysis
    eco = build_complete_evolutionary_analysis(scenario="integrated_risk", seed=42)
    assert "bioinsumos_goticulas" in eco["modules"]
    assert "leite_web3" in eco["modules"]
    assert "manejo_agropecuario" not in eco["modules"]
    assert "ecosystem_evidence_hash" in eco["web3_layer"]
    ev = build_complete_ecosystem_evidence(eco)
    assert ev["evidence_type"] == "complete_ecosystem_simulation"
    assert len(ev["hash"]) == 64
