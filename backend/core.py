"""
Nucleo do MVP HackWeb 3.0 - Analise Evolutiva.
Simula a cadeia produtiva do leite, a leitura espectral por espectrofotometro,
a classificacao por regras/IA simplificada e a geracao de evidencia rastreavel.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

SPECTRAL_CHANNELS_NM = [415, 445, 480, 515, 555, 590, 630, 680, 730, 850, 910]


@dataclass(frozen=True)
class ChainStage:
    etapa: str
    responsavel: str
    local: str
    timestamp_utc: str
    observacao: str


@dataclass(frozen=True)
class MilkAnalysis:
    classificacao: str
    score_conformidade: float
    score_adulteracao: float
    parametros: Dict[str, float]
    recomendacao: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(data: Dict[str, Any] | str) -> str:
    if isinstance(data, dict):
        data = canonical_json(data)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def simulate_spectral_reading(seed: Optional[int] = None, adulterated: Optional[bool] = None) -> Dict[str, Any]:
    """Gera uma leitura multiespectral plausivel para demonstracao.

    A simulacao nao substitui calibracao laboratorial. Ela serve para o MVP: demonstrar
    o fluxo de aquisicao, analise, hash, registro e verificacao.
    """
    rng = random.Random(seed)
    if adulterated is None:
        adulterated = rng.random() < 0.28

    base = {
        415: 0.78, 445: 0.81, 480: 0.84, 515: 0.86, 555: 0.88,
        590: 0.85, 630: 0.79, 680: 0.73, 730: 0.69, 850: 0.61, 910: 0.56,
    }

    channels: Dict[str, float] = {}
    for nm in SPECTRAL_CHANNELS_NM:
        noise = rng.uniform(-0.025, 0.025)
        value = base[nm] + noise
        if adulterated:
            if nm in (850, 910):
                value += rng.uniform(0.08, 0.15)
            if nm in (415, 445, 480):
                value -= rng.uniform(0.03, 0.07)
        channels[str(nm)] = round(max(0.0, min(1.0, value)), 4)

    temperatura_c = round(rng.uniform(3.0, 7.8) + (rng.uniform(2.0, 5.0) if adulterated and rng.random() < 0.35 else 0), 2)
    ph = round(rng.uniform(6.55, 6.82) + (rng.uniform(-0.25, 0.18) if adulterated else 0), 2)
    condutividade_ms_cm = round(rng.uniform(4.0, 5.8) + (rng.uniform(0.8, 1.8) if adulterated else 0), 2)

    return {
        "sensor": "AS7341-simulado",
        "comprimentos_onda_nm": SPECTRAL_CHANNELS_NM,
        "leituras_normalizadas": channels,
        "temperatura_c": temperatura_c,
        "ph": ph,
        "condutividade_ms_cm": condutividade_ms_cm,
        "perfil_simulado": "adulterado" if adulterated else "conforme",
    }


def analyze_milk(reading: Dict[str, Any]) -> MilkAnalysis:
    channels = {int(k): float(v) for k, v in reading["leituras_normalizadas"].items()}
    nir_mean = (channels[850] + channels[910]) / 2
    visible_mean = sum(channels[nm] for nm in [445, 480, 515, 555, 590, 630]) / 6
    uv_visible_delta = channels[480] - channels[415]
    temp = float(reading["temperatura_c"])
    ph = float(reading["ph"])
    cond = float(reading["condutividade_ms_cm"])

    # Heuristica inicial de demonstracao: a calibracao real devera substituir estes pesos.
    adulteration_score = 0.0
    adulteration_score += max(0.0, (nir_mean - 0.66) * 2.3)
    adulteration_score += max(0.0, (cond - 5.8) * 0.18)
    adulteration_score += max(0.0, abs(ph - 6.7) - 0.16) * 1.4
    adulteration_score += max(0.0, temp - 8.0) * 0.08
    adulteration_score += max(0.0, 0.05 - uv_visible_delta) * 1.1
    adulteration_score = round(min(1.0, adulteration_score), 4)
    conformity = round(max(0.0, 1.0 - adulteration_score), 4)

    if adulteration_score >= 0.65:
        classification = "Suspeita de adulteracao"
        recommendation = "Reter lote, repetir leitura, gerar contraprova e encaminhar amostra para validacao laboratorial."
    elif adulteration_score >= 0.35:
        classification = "Atencao tecnica"
        recommendation = "Repetir medicao, conferir temperatura, limpeza da cubeta e historico do produtor antes da liberacao."
    else:
        classification = "Conforme no MVP"
        recommendation = "Lote apto para continuidade da cadeia, mantendo registro de rastreabilidade e auditoria."

    return MilkAnalysis(
        classificacao=classification,
        score_conformidade=conformity,
        score_adulteracao=adulteration_score,
        parametros={
            "media_nir_850_910": round(nir_mean, 4),
            "media_visivel": round(visible_mean, 4),
            "delta_uv_visivel": round(uv_visible_delta, 4),
            "temperatura_c": temp,
            "ph": ph,
            "condutividade_ms_cm": cond,
        },
        recomendacao=recommendation,
    )


def build_chain(sample_id: str, producer_name: str, farm_name: str, city: str) -> List[Dict[str, str]]:
    stages = [
        ChainStage("Coleta na propriedade", producer_name, farm_name, utc_now(), "Amostra vinculada ao produtor, lote e tanque de origem."),
        ChainStage("Transporte resfriado", "Transportador credenciado", city, utc_now(), "Registro de rota e condicao de conservacao."),
        ChainStage("Recebimento na cooperativa", "Cooperativa / laticinio", city, utc_now(), "Conferencia de volume, temperatura e lacre."),
        ChainStage("Analise Evolutiva", "Espectrofotometro multiespectral", "Laboratorio de campo", utc_now(), f"Leitura espectral da amostra {sample_id}."),
        ChainStage("Registro Web3", "Smart contract de rastreabilidade", "Blockchain/testnet", utc_now(), "Hash da evidencia registrado para verificacao publica."),
    ]
    return [asdict(stage) for stage in stages]


def create_sample(seed: Optional[int] = None, producer_name: str = "Produtor demonstrativo", farm_name: str = "Fazenda Piloto", city: str = "Goiás", adulterated: Optional[bool] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    timestamp = utc_now()
    sample_id = f"AE-LEITE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{rng.randint(1000, 9999)}"
    lot_id = f"LOTE-{rng.randint(100, 999)}-{rng.choice(['A', 'B', 'C'])}"
    tank_id = f"TQ-{rng.randint(1, 6):02d}"

    reading = simulate_spectral_reading(seed=seed, adulterated=adulterated)
    analysis = analyze_milk(reading)

    evidence_payload = {
        "projeto": "Analise Evolutiva HackWeb 3.0",
        "dominio": "Cadeia produtiva do leite",
        "sample_id": sample_id,
        "lot_id": lot_id,
        "tank_id": tank_id,
        "producer_name": producer_name,
        "farm_name": farm_name,
        "city": city,
        "created_at_utc": timestamp,
        "spectral_reading": reading,
        "analysis": asdict(analysis),
        "chain": build_chain(sample_id, producer_name, farm_name, city),
    }
    evidence_hash = sha256_hex(evidence_payload)
    tx_hash = "0x" + sha256_hex(f"{evidence_hash}:{timestamp}:analise-evolutiva")[:64]

    return {
        **evidence_payload,
        "evidence_hash": evidence_hash,
        "blockchain": {
            "modo": "simulado_para_mvp",
            "network": "local/testnet",
            "contract_name": "AnaliseEvolutivaLeiteTrace",
            "tx_hash": tx_hash,
            "status_onchain": "REGISTRADO",
        },
        "verification_url_path": f"/verificar/{evidence_hash}",
    }


def verify_integrity(stored_sample: Dict[str, Any]) -> Dict[str, Any]:
    payload = {k: v for k, v in stored_sample.items() if k not in {"evidence_hash", "blockchain", "verification_url_path", "id"}}
    recomputed = sha256_hex(payload)
    original = stored_sample.get("evidence_hash")
    return {
        "hash_original": original,
        "hash_recalculado": recomputed,
        "integro": original == recomputed,
    }
