"""Núcleo técnico do MVP Análise Evolutiva Web3.

O objetivo deste módulo é simular uma leitura espectrofotométrica do leite,
gerar uma análise técnica demonstrativa e produzir uma evidência digital
com hash criptográfico para rastreabilidade Web3.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping

WAVELENGTHS_NM = [415, 445, 480, 515, 555, 590, 630, 680, 910]

REFERENCE_PROFILE = {
    "415": 0.72,
    "445": 0.69,
    "480": 0.65,
    "515": 0.61,
    "555": 0.57,
    "590": 0.52,
    "630": 0.48,
    "680": 0.43,
    "910": 0.34,
}

SCENARIO_FACTORS = {
    "normal": 1.0,
    "water_adulteration": 0.82,
    "temperature_break": 0.92,
    "high_solids": 1.08,
}


@dataclass(frozen=True)
class TraceStep:
    stage: str
    actor: str
    timestamp: str
    location: str
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class SpectralSample:
    batch_id: str
    producer_id: str
    producer_name: str
    collection_point: str
    cooperative: str
    equipment_id: str
    scenario: str
    temperature_celsius: float
    spectral_reading: Dict[str, float]
    traceability: List[TraceStep]


@dataclass(frozen=True)
class AnalysisResult:
    status: str
    compliance_score: float
    spectral_consistency: float
    water_adulteration_risk: float
    temperature_risk: float
    solids_index: float
    recommendation: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(payload: Mapping[str, Any]) -> str:
    """Retorna JSON canônico para cálculo de hash estável."""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_payload(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _bounded(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def simulate_spectral_reading(scenario: str = "normal", seed: int | None = None) -> SpectralSample:
    """Gera uma amostra simulada de leitura espectrofotométrica.

    Cenários aceitos:
    - normal
    - water_adulteration
    - temperature_break
    - high_solids
    """
    if scenario not in SCENARIO_FACTORS:
        raise ValueError(f"Cenário inválido: {scenario}")

    rng = random.Random(seed)
    factor = SCENARIO_FACTORS[scenario]
    spectral: Dict[str, float] = {}

    for wavelength in WAVELENGTHS_NM:
        base = REFERENCE_PROFILE[str(wavelength)]
        noise = rng.uniform(-0.018, 0.018)
        if scenario == "water_adulteration" and wavelength in (680, 910):
            noise -= 0.035
        if scenario == "high_solids" and wavelength in (415, 445, 480):
            noise += 0.025
        spectral[str(wavelength)] = round(_bounded(base * factor + noise, 0.05, 1.25), 4)

    temperature = {
        "normal": rng.uniform(3.2, 5.5),
        "water_adulteration": rng.uniform(4.0, 6.2),
        "temperature_break": rng.uniform(9.0, 13.5),
        "high_solids": rng.uniform(3.0, 5.0),
    }[scenario]

    batch_id = f"LEITE-{datetime.now().strftime('%Y%m%d')}-{rng.randint(1000, 9999)}"
    producer_id = f"PROD-{rng.randint(100, 999)}"
    now = utc_now()

    traceability = [
        TraceStep(
            stage="coleta",
            actor="Produtor rural",
            timestamp=now,
            location="Propriedade leiteira simulada",
            metadata={"volume_litros": rng.randint(900, 2200), "tanque": f"TQ-{rng.randint(1, 6)}"},
        ),
        TraceStep(
            stage="transporte",
            actor="Transportador credenciado",
            timestamp=now,
            location="Rota refrigerada",
            metadata={"temperatura_media_celsius": round(temperature, 2), "veiculo": f"TR-{rng.randint(10, 99)}"},
        ),
        TraceStep(
            stage="recebimento",
            actor="Cooperativa/Laboratório",
            timestamp=now,
            location="Unidade de análise",
            metadata={"conferencia_lacre": True, "amostra_integral": True},
        ),
        TraceStep(
            stage="analise_espectrofotometrica",
            actor="Análise Evolutiva",
            timestamp=now,
            location="Bancada de análise multiespectral",
            metadata={"sensor": "AS7341/Simulado", "faixa_nm": "415-910"},
        ),
    ]

    return SpectralSample(
        batch_id=batch_id,
        producer_id=producer_id,
        producer_name="Produtor demonstrativo",
        collection_point="Ponto de coleta demonstrativo",
        cooperative="Cooperativa demonstrativa",
        equipment_id="AE-SPEC-MVP-001",
        scenario=scenario,
        temperature_celsius=round(temperature, 2),
        spectral_reading=spectral,
        traceability=traceability,
    )


def sample_to_dict(sample: SpectralSample) -> Dict[str, Any]:
    data = asdict(sample)
    return data


def analyze_milk_sample(sample: Mapping[str, Any]) -> AnalysisResult:
    spectral = sample.get("spectral_reading") or {}
    if not spectral:
        raise ValueError("A amostra não possui leitura espectrofotométrica.")

    deviations = []
    for key, ref in REFERENCE_PROFILE.items():
        value = float(spectral.get(key, ref))
        deviations.append(abs(value - ref) / max(ref, 0.001))

    mean_deviation = sum(deviations) / len(deviations)
    spectral_consistency = _bounded(1 - mean_deviation)

    ratio_910_630 = float(spectral.get("910", 0.0)) / max(float(spectral.get("630", 1.0)), 0.001)
    expected_ratio = REFERENCE_PROFILE["910"] / REFERENCE_PROFILE["630"]
    water_adulteration_risk = _bounded((expected_ratio - ratio_910_630) * 2.2 + mean_deviation * 0.8)

    temperature = float(sample.get("temperature_celsius", 4.0))
    temperature_risk = _bounded((temperature - 6.0) / 8.0)

    solids_index = _bounded((float(spectral.get("415", 0.72)) + float(spectral.get("445", 0.69)) + float(spectral.get("480", 0.65))) / 2.1)

    compliance_score = _bounded(
        0.55 * spectral_consistency
        + 0.25 * (1 - water_adulteration_risk)
        + 0.20 * (1 - temperature_risk)
    )

    if compliance_score >= 0.86 and water_adulteration_risk < 0.18 and temperature_risk < 0.18:
        status = "APROVADO"
        recommendation = "Lote aprovado para continuidade na cadeia produtiva. Manter rastreabilidade e evidência registrada."
    elif compliance_score >= 0.70:
        status = "ATENÇÃO"
        recommendation = "Lote requer revisão técnica, conferência de temperatura e possível contraprova laboratorial."
    else:
        status = "REPROVADO"
        recommendation = "Lote deve ser bloqueado preventivamente e encaminhado para investigação/contraprova."

    return AnalysisResult(
        status=status,
        compliance_score=round(compliance_score, 4),
        spectral_consistency=round(spectral_consistency, 4),
        water_adulteration_risk=round(water_adulteration_risk, 4),
        temperature_risk=round(temperature_risk, 4),
        solids_index=round(solids_index, 4),
        recommendation=recommendation,
    )


def build_evidence(sample: Mapping[str, Any], analysis: AnalysisResult) -> Dict[str, Any]:
    evidence_id = str(uuid.uuid4())
    payload = {
        "evidence_id": evidence_id,
        "project": "Análise Evolutiva Web3 — Cadeia Produtiva do Leite",
        "version": "1.0.0-hackweb3",
        "created_at": utc_now(),
        "sample": sample,
        "analysis": asdict(analysis),
        "web3": {
            "hash_algorithm": "SHA-256",
            "storage_strategy": "off-chain evidence + on-chain hash",
            "privacy_note": "A blockchain registra a prova de integridade, não o laudo completo.",
        },
    }
    evidence_hash = sha256_payload(payload)
    payload["evidence_hash"] = evidence_hash
    return payload


def build_demo_evidence(scenario: str = "normal", seed: int | None = 42) -> Dict[str, Any]:
    sample = sample_to_dict(simulate_spectral_reading(scenario=scenario, seed=seed))
    analysis = analyze_milk_sample(sample)
    return build_evidence(sample, analysis)


def tamper_check(evidence: Mapping[str, Any]) -> bool:
    """Verifica se o hash salvo ainda corresponde ao conteúdo da evidência."""
    expected = evidence.get("evidence_hash")
    if not expected:
        return False
    cloned = dict(evidence)
    cloned.pop("evidence_hash", None)
    # Campos adicionados pela camada de persistência/Web3 não participam do hash original.
    cloned.pop("transaction_hash", None)
    cloned.pop("blockchain_mode", None)
    return sha256_payload(cloned) == expected


def risk_label(value: float) -> str:
    if value < 0.20:
        return "baixo"
    if value < 0.45:
        return "moderado"
    return "alto"


def format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def spectral_distance(sample: Mapping[str, Any]) -> float:
    spectral = sample.get("spectral_reading") or {}
    total = 0.0
    for key, ref in REFERENCE_PROFILE.items():
        total += (float(spectral.get(key, ref)) - ref) ** 2
    return round(math.sqrt(total), 5)
