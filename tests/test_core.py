from backend.core import (
    analyze_milk_sample,
    build_demo_evidence,
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
