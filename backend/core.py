"""Núcleo técnico do MVP Análise Evolutiva Web3.

Este módulo simula, de forma demonstrativa, o fluxo completo da cadeia
produtiva do leite com espectrofotometria multiespectral: solo/pastagem,
alimentação do rebanho, água, coleta do leite, leitura óptica, análise
pela Análise Evolutiva, geração de evidência digital e rastreabilidade Web3.

A simulação usa dados sintéticos. Ela não substitui calibração laboratorial,
curvas reais de referência, validação metrológica ou laudo oficial.
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

# Faixa demonstrativa do protótipo citado para a Análise Evolutiva: UV/VIS/NIR.
# O AS7341 cobre canais visíveis e NIR; para o MVP, os canais UV e NIR adicionais
# representam bancos ópticos/LEDs externos simulados no protótipo completo.
WAVELENGTHS_NM = [365, 395, 415, 445, 480, 515, 555, 590, 630, 680, 730, 760, 810, 860, 910]
MILK_WAVELENGTHS_NM = [415, 445, 480, 515, 555, 590, 630, 680, 730, 760, 810, 860, 910]

SPECTROMETER_CONFIG: Dict[str, Any] = {
    "equipment_id": "AE-SPEC-V11-MVP-001",
    "serial_number": "AE-SPEC-UVVISNIR-0001-MVP",
    "firmware": "ae-spec-fw 0.9.7-mvp",
    "sensor_stack": "AS7341 11 canais + extensão UV/NIR simulada",
    "optical_geometry": "transmitância em cubeta 10 mm + reflectância demonstrativa para solo/alimentação",
    "optical_path_mm": 10,
    "light_banks": ["UV 365/395 nm", "VIS 415-680 nm", "NIR 730-910 nm"],
    "detector": "fotodiodos multicanais com ADC 16 bits",
    "microcontroller": "ESP32 com envio HTTP/JSON",
    "integration_time_ms": 120,
    "gain": "64x",
    "adc_resolution_bits": 16,
    "adc_full_scale": 65535,
    "communication": "ESP32/HTTP JSON para servidor Flask",
    "calibration_strategy": "auto-teste + corrente escura + branco/referência + normalização por canal + QC por saturação/SNR",
    "sample_handling": "gaveta/câmara escura simulada, cubeta para líquidos e suporte óptico para solo/alimentação",
}

SPECTROMETER_WORKFLOW = [
    "Inicialização do ESP32, sensor óptico e bancos de LED",
    "Auto-teste de comunicação, câmara escura, detector e alimentação",
    "Estabilização térmica e verificação de ruído eletrônico",
    "Captura de corrente escura com LEDs desligados",
    "Captura do branco/referência óptica",
    "Inserção da amostra e travamento da câmara",
    "Varredura sequencial UV/VIS/NIR por comprimento de onda",
    "Correção do ADC, normalização, absorbância/reflectância e controle de qualidade",
    "Envio do pacote JSON para a Análise Evolutiva e geração da evidência",
]

# Perfil de transmitância de leite cru refrigerado em cenário demonstrativo.
REFERENCE_PROFILE = {
    "415": 0.72,
    "445": 0.69,
    "480": 0.65,
    "515": 0.61,
    "555": 0.57,
    "590": 0.52,
    "630": 0.48,
    "680": 0.43,
    "730": 0.39,
    "760": 0.37,
    "810": 0.35,
    "860": 0.34,
    "910": 0.33,
}

SOIL_REFERENCE_PROFILE = {
    "365": 0.18,
    "395": 0.20,
    "415": 0.24,
    "445": 0.27,
    "480": 0.31,
    "515": 0.34,
    "555": 0.37,
    "590": 0.40,
    "630": 0.43,
    "680": 0.45,
    "730": 0.48,
    "760": 0.51,
    "810": 0.54,
    "860": 0.56,
    "910": 0.58,
}

FEED_REFERENCE_PROFILE = {
    "365": 0.22,
    "395": 0.26,
    "415": 0.32,
    "445": 0.36,
    "480": 0.41,
    "515": 0.45,
    "555": 0.49,
    "590": 0.53,
    "630": 0.57,
    "680": 0.60,
    "730": 0.64,
    "760": 0.67,
    "810": 0.70,
    "860": 0.72,
    "910": 0.74,
}

WATER_REFERENCE_PROFILE = {
    "365": 0.74,
    "395": 0.78,
    "415": 0.82,
    "445": 0.85,
    "480": 0.88,
    "515": 0.90,
    "555": 0.92,
    "590": 0.93,
    "630": 0.94,
    "680": 0.95,
    "730": 0.96,
    "760": 0.96,
    "810": 0.95,
    "860": 0.95,
    "910": 0.94,
}

SCENARIO_FACTORS = {
    "normal": 1.0,
    "water_adulteration": 1.10,
    "temperature_break": 0.92,
    "high_solids": 0.90,
    "feed_risk": 0.98,
    "soil_moisture_stress": 0.97,
    "integrated_risk": 0.88,
}

SCENARIO_LABELS = {
    "normal": "Cadeia em conformidade",
    "water_adulteration": "Suspeita de adição de água no leite",
    "temperature_break": "Quebra da cadeia fria",
    "high_solids": "Leite com sólidos elevados",
    "feed_risk": "Risco na alimentação do rebanho",
    "soil_moisture_stress": "Estresse de solo/pastagem",
    "integrated_risk": "Risco integrado na cadeia",
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


def _scenario_rng(seed: int | None, scenario: str, salt: int = 0) -> random.Random:
    if seed is None:
        return random.Random()
    return random.Random(int(seed) + sum(ord(c) for c in scenario) + salt)


def _scenario_adjusted_profile(kind: str, scenario: str) -> Dict[str, float]:
    if kind == "milk":
        profile = dict(REFERENCE_PROFILE)
        if scenario == "water_adulteration":
            # Diluição reduz espalhamento/turbidez: mais transmitância em VIS/NIR,
            # menor proxy de sólidos. É uma aproximação didática para o MVP.
            for wl in profile:
                multiplier = 1.08 if int(wl) < 700 else 1.16
                profile[wl] = _bounded(profile[wl] * multiplier, 0.05, 0.98)
        elif scenario == "temperature_break":
            for wl in profile:
                profile[wl] = _bounded(profile[wl] * (0.94 if int(wl) < 700 else 0.90), 0.05, 0.98)
        elif scenario == "high_solids":
            for wl in profile:
                profile[wl] = _bounded(profile[wl] * (0.88 if int(wl) < 700 else 0.84), 0.05, 0.98)
        elif scenario == "integrated_risk":
            for wl in profile:
                profile[wl] = _bounded(profile[wl] * (1.05 if int(wl) < 700 else 1.10), 0.05, 0.98)
        return profile

    if kind == "soil":
        profile = dict(SOIL_REFERENCE_PROFILE)
        if scenario in {"soil_moisture_stress", "integrated_risk"}:
            for wl in profile:
                # Solo mais úmido/compactado tende a refletir menos em NIR no modelo demonstrativo.
                profile[wl] = _bounded(profile[wl] * (0.86 if int(wl) >= 730 else 0.92), 0.03, 0.95)
        return profile

    if kind == "feed":
        profile = dict(FEED_REFERENCE_PROFILE)
        if scenario in {"feed_risk", "integrated_risk"}:
            for wl in profile:
                # Alimentação com umidade/fermentação irregular: queda em NIR e sinal UV alterado.
                profile[wl] = _bounded(profile[wl] * (0.82 if int(wl) >= 730 else 0.94), 0.03, 0.95)
            profile["365"] = _bounded(profile["365"] * 1.18, 0.03, 0.95)
            profile["395"] = _bounded(profile["395"] * 1.15, 0.03, 0.95)
        return profile

    if kind == "water":
        profile = dict(WATER_REFERENCE_PROFILE)
        if scenario in {"soil_moisture_stress", "integrated_risk"}:
            for wl in profile:
                profile[wl] = _bounded(profile[wl] * (0.88 if int(wl) < 700 else 0.93), 0.03, 0.98)
        return profile

    raise ValueError(f"Tipo de amostra inválido: {kind}")


def simulate_wave_capture(
    reference_profile: Mapping[str, float],
    scenario: str,
    kind: str,
    seed: int | None = None,
) -> Dict[str, Any]:
    """Simula a captura óptica completa por canal.

    Para cada comprimento de onda, o simulador cria corrente escura, leitura de
    branco/referência, ADC bruto da amostra, sinal corrigido, normalização,
    transmitância/reflectância e absorbância.
    """
    rng = _scenario_rng(seed, scenario, salt={"milk": 11, "soil": 23, "feed": 37, "water": 41}.get(kind, 0))
    channels: List[Dict[str, Any]] = []
    normalized: Dict[str, float] = {}
    absorbance: Dict[str, float] = {}

    for wl_str, target_value in reference_profile.items():
        wl = int(wl_str)
        led_power = rng.uniform(0.92, 1.06)
        sensor_sensitivity = 1.0 - min(abs(wl - 555) / 1600.0, 0.22)
        dark_current = rng.uniform(80, 180)
        reference_adc = (52000 * led_power * sensor_sensitivity) + rng.uniform(-600, 600)
        physical_value = _bounded(target_value + rng.uniform(-0.018, 0.018), 0.015, 0.985)
        sample_adc = dark_current + (reference_adc - dark_current) * physical_value + rng.uniform(-180, 180)
        corrected = max(sample_adc - dark_current, 1.0)
        denominator = max(reference_adc - dark_current, 1.0)
        norm = _bounded(corrected / denominator, 0.001, 1.0)
        abs_value = -math.log10(max(norm, 0.001))

        normalized[wl_str] = round(norm, 4)
        absorbance[wl_str] = round(abs_value, 4)
        led_bank = "UV" if wl < 400 else "VIS" if wl < 700 else "NIR"
        led_current_ma = rng.uniform(18, 28) if led_bank == "UV" else rng.uniform(10, 22) if led_bank == "VIS" else rng.uniform(24, 38)
        exposure_ms = SPECTROMETER_CONFIG["integration_time_ms"] + rng.uniform(-8, 8)
        adc_full_scale_pct = _bounded(sample_adc / SPECTROMETER_CONFIG["adc_full_scale"], 0, 1)
        electronic_noise = rng.uniform(12, 42)
        snr_db = 20 * math.log10(max(corrected, 1.0) / electronic_noise)
        qc_label = "SATURADO" if sample_adc >= 65000 else "BAIXO SINAL" if snr_db < 38 else "OK"
        channels.append(
            {
                "wavelength_nm": wl,
                "led_bank": led_bank,
                "light_source": f"LED {led_bank} {wl} nm",
                "led_current_ma": round(led_current_ma, 2),
                "exposure_ms": round(exposure_ms, 2),
                "detector_channel": f"CH-{wl}",
                "dark_adc": round(dark_current, 2),
                "reference_adc": round(reference_adc, 2),
                "sample_adc": round(sample_adc, 2),
                "corrected_adc": round(corrected, 2),
                "adc_full_scale_pct": round(adc_full_scale_pct, 4),
                "normalized_signal": round(norm, 4),
                "absorbance": round(abs_value, 4),
                "snr_db": round(snr_db, 2),
                "qc_label": qc_label,
                "saturation": sample_adc >= 65000,
            }
        )

    return {
        "kind": kind,
        "scenario": scenario,
        "capture_id": f"CAP-{uuid.uuid4().hex[:12].upper()}",
        "captured_at": utc_now(),
        "spectrometer": SPECTROMETER_CONFIG,
        "calibration": {
            "dark_reference": "capturada antes da amostra",
            "white_reference": "cubeta/referência óptica do ensaio",
            "temperature_compensation": True,
            "stray_light_correction": "simulada por canal",
        },
        "channels": channels,
        "normalized_signal": normalized,
        "absorbance": absorbance,
    }


def _temperature_for_scenario(scenario: str, rng: random.Random) -> float:
    return {
        "normal": rng.uniform(3.2, 5.5),
        "water_adulteration": rng.uniform(4.0, 6.2),
        "temperature_break": rng.uniform(9.0, 13.5),
        "high_solids": rng.uniform(3.0, 5.0),
        "feed_risk": rng.uniform(4.0, 6.5),
        "soil_moisture_stress": rng.uniform(3.5, 6.0),
        "integrated_risk": rng.uniform(8.0, 12.5),
    }[scenario]


def simulate_spectral_reading(scenario: str = "normal", seed: int | None = None) -> SpectralSample:
    """Gera uma amostra simulada de leitura espectrofotométrica do leite."""
    if scenario not in SCENARIO_FACTORS:
        raise ValueError(f"Cenário inválido: {scenario}")

    rng = _scenario_rng(seed, scenario, salt=101)
    milk_profile = _scenario_adjusted_profile("milk", scenario)
    capture = simulate_wave_capture(milk_profile, scenario=scenario, kind="milk", seed=seed)
    spectral = {wl: capture["normalized_signal"][wl] for wl in REFERENCE_PROFILE.keys()}
    temperature = _temperature_for_scenario(scenario, rng)

    batch_id = f"LEITE-{datetime.now().strftime('%Y%m%d')}-{rng.randint(1000, 9999)}"
    producer_id = f"PROD-{rng.randint(100, 999)}"
    now = utc_now()

    traceability = [
        TraceStep(
            stage="solo_pastagem",
            actor="Análise Evolutiva",
            timestamp=now,
            location="Talhão de pastagem demonstrativo",
            metadata={"sensores": ["NPK", "pH", "umidade", "espectrofotometria"], "finalidade": "contexto produtivo"},
        ),
        TraceStep(
            stage="alimentacao_rebanho",
            actor="Análise Evolutiva",
            timestamp=now,
            location="Cocho/silo demonstrativo",
            metadata={"amostra": "silagem/ração", "finalidade": "risco de umidade e qualidade nutricional"},
        ),
        TraceStep(
            stage="coleta_leite",
            actor="Produtor rural",
            timestamp=now,
            location="Propriedade leiteira simulada",
            metadata={"volume_litros": rng.randint(900, 2200), "tanque": f"TQ-{rng.randint(1, 6)}"},
        ),
        TraceStep(
            stage="transporte_refrigerado",
            actor="Transportador credenciado",
            timestamp=now,
            location="Rota refrigerada",
            metadata={"temperatura_media_celsius": round(temperature, 2), "veiculo": f"TR-{rng.randint(10, 99)}"},
        ),
        TraceStep(
            stage="analise_espectrofotometrica",
            actor="Análise Evolutiva",
            timestamp=now,
            location="Bancada de análise multiespectral",
            metadata={"sensor": SPECTROMETER_CONFIG["sensor_stack"], "faixa_nm": "365-910"},
        ),
    ]

    return SpectralSample(
        batch_id=batch_id,
        producer_id=producer_id,
        producer_name="Produtor demonstrativo",
        collection_point="Ponto de coleta demonstrativo",
        cooperative="Cooperativa demonstrativa",
        equipment_id=SPECTROMETER_CONFIG["equipment_id"],
        scenario=scenario,
        temperature_celsius=round(temperature, 2),
        spectral_reading=spectral,
        traceability=traceability,
    )


def sample_to_dict(sample: SpectralSample) -> Dict[str, Any]:
    return asdict(sample)


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
    # Quanto maior a distância do padrão, maior a suspeita. O sinal é demonstrativo.
    water_adulteration_risk = _bounded(abs(ratio_910_630 - expected_ratio) * 1.6 + mean_deviation * 0.45)

    temperature = float(sample.get("temperature_celsius", 4.0))
    temperature_risk = _bounded((temperature - 6.0) / 8.0)

    solids_index = _bounded(1 - ((float(spectral.get("810", 0.35)) + float(spectral.get("860", 0.34)) + float(spectral.get("910", 0.33))) / 3.0 - 0.30))

    compliance_score = _bounded(
        0.48 * spectral_consistency
        + 0.25 * (1 - water_adulteration_risk)
        + 0.17 * (1 - temperature_risk)
        + 0.10 * solids_index
    )

    if compliance_score >= 0.86 and water_adulteration_risk < 0.20 and temperature_risk < 0.18:
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


def _mean(values: List[float]) -> float:
    return sum(values) / max(len(values), 1)


def analyze_soil(capture: Mapping[str, Any]) -> Dict[str, Any]:
    signal = capture["normalized_signal"]
    nir = _mean([float(signal[str(wl)]) for wl in (730, 760, 810, 860, 910)])
    red = float(signal["680"])
    green = float(signal["555"])
    uv = _mean([float(signal["365"]), float(signal["395"])])
    moisture_risk = _bounded((0.50 - nir) * 1.8)
    organic_matter_proxy = _bounded(1 - _mean([red, green, uv]))
    pasture_support_score = _bounded(0.55 * (1 - moisture_risk) + 0.45 * organic_matter_proxy)
    return {
        "sample_type": "solo/pastagem",
        "moisture_risk": round(moisture_risk, 4),
        "organic_matter_proxy": round(organic_matter_proxy, 4),
        "pasture_support_score": round(pasture_support_score, 4),
        "interpretation": "Solo com suporte adequado à pastagem" if pasture_support_score >= 0.55 else "Solo exige atenção em umidade/matéria orgânica",
    }


def analyze_feed(capture: Mapping[str, Any]) -> Dict[str, Any]:
    signal = capture["normalized_signal"]
    uv_signal = _mean([float(signal["365"]), float(signal["395"])])
    nir_signal = _mean([float(signal[str(wl)]) for wl in (760, 810, 860, 910)])
    dry_matter_proxy = _bounded(nir_signal)
    fermentation_risk = _bounded((0.64 - nir_signal) * 1.7 + max(uv_signal - 0.25, 0) * 0.8)
    nutrition_score = _bounded(0.72 * dry_matter_proxy + 0.28 * (1 - fermentation_risk))
    return {
        "sample_type": "alimentação do rebanho",
        "dry_matter_proxy": round(dry_matter_proxy, 4),
        "fermentation_or_mold_risk": round(fermentation_risk, 4),
        "nutrition_score": round(nutrition_score, 4),
        "interpretation": "Alimentação dentro do padrão demonstrativo" if nutrition_score >= 0.60 else "Alimentação exige avaliação de umidade/fermentação",
    }


def analyze_water(capture: Mapping[str, Any]) -> Dict[str, Any]:
    signal = capture["normalized_signal"]
    visible_transparency = _mean([float(signal[str(wl)]) for wl in (415, 445, 480, 515, 555, 590, 630)])
    uv_organic_signal = 1 - _mean([float(signal["365"]), float(signal["395"])])
    turbidity_risk = _bounded((0.90 - visible_transparency) * 2.2)
    water_score = _bounded(0.65 * (1 - turbidity_risk) + 0.35 * (1 - uv_organic_signal))
    return {
        "sample_type": "água de consumo/limpeza",
        "visible_transparency": round(visible_transparency, 4),
        "organic_signal_proxy": round(uv_organic_signal, 4),
        "turbidity_risk": round(turbidity_risk, 4),
        "water_score": round(water_score, 4),
        "interpretation": "Água compatível com controle operacional" if water_score >= 0.70 else "Água exige atenção em transparência/sinal orgânico",
    }



def _capture_quality_summary(capture: Mapping[str, Any]) -> Dict[str, Any]:
    channels = capture.get("channels", [])
    saturated = sum(1 for ch in channels if ch.get("saturation"))
    low_signal = sum(1 for ch in channels if ch.get("qc_label") == "BAIXO SINAL")
    snr_values = [float(ch.get("snr_db", 0)) for ch in channels]
    fs_values = [float(ch.get("adc_full_scale_pct", 0)) for ch in channels]
    mean_snr = _mean(snr_values)
    mean_full_scale = _mean(fs_values)
    valid = saturated == 0 and low_signal == 0 and mean_snr >= 38
    return {
        "valid_capture": valid,
        "saturated_channels": saturated,
        "low_signal_channels": low_signal,
        "mean_snr_db": round(mean_snr, 2),
        "mean_adc_full_scale_pct": round(mean_full_scale, 4),
        "qc_label": "CAPTURA VÁLIDA" if valid else "REVISAR CAPTURA",
    }



def build_live_capture_sequence(session: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Cria uma sequência operacional para simular a captura real do espectrofotômetro.

    A sequência não é apenas o resultado final: ela representa o que o
    equipamento faria na bancada, em ordem temporal: energização, auto-teste,
    calibração escura, branco de referência, acionamento de cada LED, leitura
    ADC, cálculo de absorbância, fechamento do pacote JSON e envio para a
    camada de análise/rastreabilidade.
    """

    def event(
        order: int,
        phase: str,
        message: str,
        *,
        matrix: str | None = None,
        kind: str | None = None,
        wavelength_nm: int | None = None,
        led_bank: str | None = None,
        led_state: str = "OFF",
        led_current_ma: float | None = None,
        exposure_ms: float | None = None,
        dark_adc: float | None = None,
        reference_adc: float | None = None,
        sample_adc: float | None = None,
        corrected_adc: float | None = None,
        normalized_signal: float | None = None,
        absorbance: float | None = None,
        snr_db: float | None = None,
        qc_label: str | None = None,
        duration_ms: int = 70,
    ) -> Dict[str, Any]:
        return {
            "event_id": f"EVT-{order:04d}",
            "order": order,
            "phase": phase,
            "matrix": matrix,
            "kind": kind,
            "message": message,
            "wavelength_nm": wavelength_nm,
            "led_bank": led_bank,
            "led_state": led_state,
            "led_current_ma": led_current_ma,
            "exposure_ms": exposure_ms,
            "dark_adc": dark_adc,
            "reference_adc": reference_adc,
            "sample_adc": sample_adc,
            "corrected_adc": corrected_adc,
            "normalized_signal": normalized_signal,
            "absorbance": absorbance,
            "snr_db": snr_db,
            "qc_label": qc_label,
            "duration_ms": duration_ms,
        }

    events: List[Dict[str, Any]] = []
    order = 1
    events.append(event(order, "POWER_ON", "Energizando ESP32, sensor multicanal, detector e bancos de LED.", duration_ms=120)); order += 1
    events.append(event(order, "BOOT", f"Firmware carregado: {session['equipment']['firmware']}.", duration_ms=90)); order += 1
    for test in session.get("self_test", []):
        events.append(event(order, "SELF_TEST", f"Auto-teste: {test['item']} — {test['status']} ({test['detail']}).", duration_ms=85)); order += 1
    events.append(event(order, "THERMAL_STABILIZATION", "Estabilizando câmara óptica, ganho do detector e ruído eletrônico.", duration_ms=120)); order += 1

    for cycle in session.get("sample_cycles", []):
        matrix = cycle["matrix"]
        kind = cycle["kind"]
        events.append(event(order, "SAMPLE_INSERT", f"Inserindo {matrix} no {cycle['container']}: {cycle['sample_preparation']}.", matrix=matrix, kind=kind, duration_ms=120)); order += 1
        events.append(event(order, "CHAMBER_LOCK", "Travando câmara escura e bloqueando luz ambiente.", matrix=matrix, kind=kind, duration_ms=80)); order += 1
        mean_dark = round(_mean([float(ch.get("dark_adc", 0)) for ch in cycle.get("led_sweep", [])]), 2)
        events.append(event(order, "DARK_CAPTURE", f"Capturando corrente escura de {matrix} com todos os LEDs desligados.", matrix=matrix, kind=kind, dark_adc=mean_dark, led_state="OFF", duration_ms=100)); order += 1
        events.append(event(order, "WHITE_REFERENCE", f"Capturando branco/referência óptica para normalização de {matrix}.", matrix=matrix, kind=kind, duration_ms=100)); order += 1

        for ch in cycle.get("led_sweep", []):
            wl = int(ch["wavelength_nm"])
            led_bank = "UV" if wl < 400 else "VIS" if wl < 700 else "NIR"
            corrected = round(float(ch.get("sample_adc", 0)) - float(ch.get("dark_adc", 0)), 2)
            msg = (
                f"LED {led_bank} {wl} nm acionado; integração {ch.get('exposure_ms')} ms; "
                f"ADC da amostra={ch.get('sample_adc')}; sinal normalizado={ch.get('normalized_signal')}."
            )
            events.append(event(
                order, "CHANNEL_CAPTURE", msg,
                matrix=matrix, kind=kind, wavelength_nm=wl, led_bank=led_bank, led_state="ON",
                led_current_ma=ch.get("led_current_ma"), exposure_ms=ch.get("exposure_ms"),
                dark_adc=ch.get("dark_adc"), reference_adc=ch.get("reference_adc"), sample_adc=ch.get("sample_adc"),
                corrected_adc=corrected, normalized_signal=ch.get("normalized_signal"), absorbance=ch.get("absorbance"),
                snr_db=ch.get("snr_db"), qc_label=ch.get("qc_label"), duration_ms=55,
            )); order += 1

        qc = cycle.get("quality_control", {})
        events.append(event(order, "MATRIX_QC", f"Controle de qualidade de {matrix}: {qc.get('qc_label')} — SNR médio {qc.get('mean_snr_db')} dB.", matrix=matrix, kind=kind, qc_label=qc.get("qc_label"), duration_ms=90)); order += 1
        events.append(event(order, "PACKET_READY", f"Pacote JSON de {matrix} pronto para envio HTTP ao backend Flask.", matrix=matrix, kind=kind, duration_ms=70)); order += 1

    events.append(event(order, "ANALYSIS", "A Análise Evolutiva recebe os pacotes, integra leite, solo, água e alimentação e gera diagnóstico técnico.", duration_ms=110)); order += 1
    events.append(event(order, "EVIDENCE_HASH", "Evidência digital completa montada off-chain; cálculo do hash SHA-256 para rastreabilidade.", duration_ms=95)); order += 1
    events.append(event(order, "WEB3_REGISTER", "Hash preparado para registro Web3/smart contract e verificação pública.", duration_ms=95)); order += 1

    return events

def build_spectrophotometer_session(
    captures: Mapping[str, Mapping[str, Any]],
    scenario: str,
    seed: int | None = None,
) -> Dict[str, Any]:
    """Monta uma sessão completa do espectrofotômetro para demonstração do hardware.

    A sessão simula a experiência que o avaliador/investidor precisa enxergar:
    inicialização do equipamento, auto-teste, calibração, inserção de amostras,
    varredura por LEDs, leitura ADC, controle de qualidade e envio do pacote JSON.
    """
    rng = _scenario_rng(seed, scenario, salt=909)
    session_id = f"AE-SPEC-SESSION-{datetime.now().strftime('%Y%m%d')}-{rng.randint(10000,99999)}"
    chamber_temp = rng.uniform(24.0, 28.5)
    chamber_humidity = rng.uniform(42.0, 58.0)
    supply_voltage = rng.uniform(4.86, 5.08)
    dark_noise_adc = rng.uniform(95, 160)
    drift_pct = rng.uniform(0.12, 0.68)

    self_test = [
        {"item": "ESP32 e comunicação HTTP", "status": "OK", "detail": "endpoint local Flask acessível"},
        {"item": "Sensor multicanal", "status": "OK", "detail": "canais UV/VIS/NIR respondendo"},
        {"item": "Bancos de LED", "status": "OK", "detail": "corrente e potência dentro da faixa simulada"},
        {"item": "Câmara escura", "status": "OK", "detail": f"ruído escuro médio {dark_noise_adc:.1f} ADC"},
        {"item": "Referência óptica", "status": "OK", "detail": f"deriva simulada {drift_pct:.2f}%"},
    ]

    matrix_labels = {
        "soil": "Solo/Pastagem",
        "feed": "Alimentação do rebanho",
        "water": "Água de consumo/limpeza",
        "milk": "Leite cru refrigerado",
    }
    preparation = {
        "soil": "amostra homogeneizada em suporte de reflectância demonstrativo",
        "feed": "silagem/ração triturada em porta-amostra óptico",
        "water": "cubeta limpa com branco de referência",
        "milk": "cubeta de 10 mm com leite homogeneizado e temperatura registrada",
    }
    measurement_type = {
        "soil": "reflectância aproximada",
        "feed": "reflectância aproximada",
        "water": "transmitância",
        "milk": "transmitância/absorbância",
    }

    sample_cycles = []
    for order, kind in enumerate(["soil", "feed", "water", "milk"], start=1):
        capture = captures[kind]
        quality = _capture_quality_summary(capture)
        led_sweep = []
        for ch in capture["channels"]:
            led_sweep.append({
                "wavelength_nm": ch["wavelength_nm"],
                "light_source": ch["light_source"],
                "led_current_ma": ch["led_current_ma"],
                "exposure_ms": ch["exposure_ms"],
                "dark_adc": ch["dark_adc"],
                "reference_adc": ch["reference_adc"],
                "sample_adc": ch["sample_adc"],
                "normalized_signal": ch["normalized_signal"],
                "absorbance": ch["absorbance"],
                "snr_db": ch["snr_db"],
                "qc_label": ch["qc_label"],
            })
        sample_cycles.append({
            "order": order,
            "kind": kind,
            "matrix": matrix_labels[kind],
            "sample_preparation": preparation[kind],
            "measurement_type": measurement_type[kind],
            "container": "cubeta 10 mm" if kind in {"water", "milk"} else "porta-amostra de bancada",
            "cycle_steps": [
                "abrir gaveta/câmara óptica",
                "posicionar amostra",
                "travar câmara escura",
                "capturar corrente escura",
                "capturar branco/referência",
                "executar varredura 365-910 nm",
                "calcular sinal corrigido e absorbância",
                "validar saturação, SNR e estabilidade",
                "enviar JSON para a Análise Evolutiva",
            ],
            "led_sweep": led_sweep,
            "quality_control": quality,
            "capture_id": capture["capture_id"],
        })

    overall_valid = all(c["quality_control"]["valid_capture"] for c in sample_cycles)
    session_payload = {
        "session_id": session_id,
        "started_at": utc_now(),
        "scenario": scenario,
        "equipment": SPECTROMETER_CONFIG,
        "workflow": SPECTROMETER_WORKFLOW,
        "telemetry": {
            "chamber_temperature_celsius": round(chamber_temp, 2),
            "relative_humidity_pct": round(chamber_humidity, 2),
            "supply_voltage_v": round(supply_voltage, 3),
            "dark_noise_adc_mean": round(dark_noise_adc, 2),
            "reference_drift_pct": round(drift_pct, 3),
            "operator_mode": "MVP demonstrativo para investidor/avaliador",
        },
        "self_test": self_test,
        "sample_cycles": sample_cycles,
        "overall_qc": {
            "status": "APTO PARA ANÁLISE" if overall_valid else "REVISAR LEITURA",
            "valid": overall_valid,
            "note": "Sessão sintética: em produção, estes controles devem ser validados por calibração metrológica e curvas laboratoriais.",
        },
    }
    session_payload["live_sequence"] = build_live_capture_sequence(session_payload)
    return session_payload


def build_full_chain_process(scenario: str = "normal", seed: int | None = None) -> Dict[str, Any]:
    """Simula o processo completo para demonstração do MVP/investidor."""
    if scenario not in SCENARIO_FACTORS:
        raise ValueError(f"Cenário inválido: {scenario}")

    rng = _scenario_rng(seed, scenario, salt=303)
    soil_capture = simulate_wave_capture(_scenario_adjusted_profile("soil", scenario), scenario, "soil", seed)
    feed_capture = simulate_wave_capture(_scenario_adjusted_profile("feed", scenario), scenario, "feed", seed)
    water_capture = simulate_wave_capture(_scenario_adjusted_profile("water", scenario), scenario, "water", seed)
    milk_capture = simulate_wave_capture(_scenario_adjusted_profile("milk", scenario), scenario, "milk", seed)
    spectrophotometer_session = build_spectrophotometer_session(
        {"soil": soil_capture, "feed": feed_capture, "water": water_capture, "milk": milk_capture},
        scenario=scenario,
        seed=seed,
    )

    milk_sample = sample_to_dict(simulate_spectral_reading(scenario, seed))
    milk_sample["spectral_reading"] = {wl: milk_capture["normalized_signal"][wl] for wl in REFERENCE_PROFILE.keys()}
    milk_sample["spectrometer_capture"] = milk_capture

    milk_analysis = asdict(analyze_milk_sample(milk_sample))
    soil_analysis = analyze_soil(soil_capture)
    feed_analysis = analyze_feed(feed_capture)
    water_analysis = analyze_water(water_capture)

    context_score = _bounded(
        0.28 * soil_analysis["pasture_support_score"]
        + 0.32 * feed_analysis["nutrition_score"]
        + 0.20 * water_analysis["water_score"]
        + 0.20 * (1 - milk_analysis["temperature_risk"])
    )
    integrated_score = _bounded(0.58 * milk_analysis["compliance_score"] + 0.42 * context_score)

    if integrated_score >= 0.84 and milk_analysis["status"] == "APROVADO":
        integrated_status = "APROVADO"
        conclusion = "A cadeia simulada apresenta coerência entre solo, alimentação, água, resfriamento e leite analisado."
    elif integrated_score >= 0.68:
        integrated_status = "ATENÇÃO"
        conclusion = "A cadeia simulada permite rastreabilidade, mas indica pontos que exigem revisão técnica antes da liberação comercial."
    else:
        integrated_status = "REPROVADO"
        conclusion = "A cadeia simulada apresenta risco integrado e o lote deve ser bloqueado preventivamente para contraprova."

    process_id = f"AE-CHAIN-{datetime.now().strftime('%Y%m%d')}-{rng.randint(10000, 99999)}"
    producer_id = milk_sample["producer_id"]
    now = utc_now()
    chain_steps = [
        {"order": 1, "stage": "Cadastro da propriedade", "actor": "Produtor/Cooperativa", "evidence": "ID do produtor, talhão, lote do rebanho e tanque", "timestamp": now},
        {"order": 2, "stage": "Solo e pastagem", "actor": "Análise Evolutiva", "evidence": "Leitura UV/VIS/NIR do solo e contexto da alimentação", "timestamp": now},
        {"order": 3, "stage": "Alimentação", "actor": "Análise Evolutiva", "evidence": "Leitura espectral de silagem/ração e proxy de matéria seca", "timestamp": now},
        {"order": 4, "stage": "Água e ambiente", "actor": "Análise Evolutiva", "evidence": "Leitura de transparência/turbidez e sinal orgânico", "timestamp": now},
        {"order": 5, "stage": "Coleta do leite", "actor": "Produtor rural", "evidence": "Volume, tanque, temperatura inicial e lacre", "timestamp": now},
        {"order": 6, "stage": "Transporte refrigerado", "actor": "Transportador", "evidence": "Temperatura média e rota", "timestamp": now},
        {"order": 7, "stage": "Bancada multiespectral", "actor": "Análise Evolutiva", "evidence": "Captura de ondas 365-910 nm, absorbância e normalização", "timestamp": now},
        {"order": 8, "stage": "Registro Web3", "actor": "Smart contract", "evidence": "Hash SHA-256 da evidência off-chain", "timestamp": now},
    ]

    return {
        "process_id": process_id,
        "scenario": scenario,
        "scenario_label": SCENARIO_LABELS[scenario],
        "created_at": now,
        "producer": {
            "producer_id": producer_id,
            "name": milk_sample["producer_name"],
            "property": "Fazenda Demonstrativa Análise Evolutiva",
            "herd_lot": f"RB-{rng.randint(10, 99)}",
            "pasture_plot": f"TL-{rng.randint(1, 8)}",
        },
        "spectrometer": SPECTROMETER_CONFIG,
        "spectrophotometer_session": spectrophotometer_session,
        "soil": {"capture": soil_capture, "analysis": soil_analysis},
        "feed": {"capture": feed_capture, "analysis": feed_analysis},
        "water": {"capture": water_capture, "analysis": water_analysis},
        "milk_sample": milk_sample,
        "milk_analysis": milk_analysis,
        "integrated_analysis": {
            "status": integrated_status,
            "integrated_score": round(integrated_score, 4),
            "context_score": round(context_score, 4),
            "conclusion": conclusion,
            "technical_note": "Resultado sintético para demonstração do MVP; a calibração real depende de curvas laboratoriais e validação metrológica.",
        },
        "chain_steps": chain_steps,
        "recommended_actions": _recommended_actions(integrated_status, soil_analysis, feed_analysis, water_analysis, milk_analysis),
    }


def _recommended_actions(status: str, soil: Mapping[str, Any], feed: Mapping[str, Any], water: Mapping[str, Any], milk: Mapping[str, Any]) -> List[str]:
    actions = ["Registrar hash da evidência para auditoria e verificação pública."]
    if soil["moisture_risk"] > 0.35:
        actions.append("Revisar manejo de umidade/compactação do solo e pastagem.")
    if feed["fermentation_or_mold_risk"] > 0.35:
        actions.append("Avaliar matéria seca, fermentação e armazenamento da alimentação do rebanho.")
    if water["turbidity_risk"] > 0.25:
        actions.append("Verificar fonte de água, limpeza de reservatório e turbidez operacional.")
    if milk["temperature_risk"] > 0.20:
        actions.append("Auditar cadeia fria entre tanque, transporte e recebimento.")
    if milk["water_adulteration_risk"] > 0.25:
        actions.append("Solicitar contraprova laboratorial para suspeita de adulteração/diluição.")
    if status == "APROVADO":
        actions.append("Liberar lote com evidência rastreável e monitoramento contínuo.")
    return actions


def build_evidence(sample: Mapping[str, Any], analysis: AnalysisResult) -> Dict[str, Any]:
    evidence_id = str(uuid.uuid4())
    payload = {
        "evidence_id": evidence_id,
        "project": "Análise Evolutiva Web3 — Cadeia Produtiva do Leite",
        "version": "1.3.0-hackweb3-live-spectrometer-capture",
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


def build_chain_evidence(process: Mapping[str, Any]) -> Dict[str, Any]:
    milk_sample = dict(process["milk_sample"])
    integrated = process["integrated_analysis"]
    evidence_id = str(uuid.uuid4())
    payload = {
        "evidence_id": evidence_id,
        "project": "Análise Evolutiva Web3 — Cadeia Produtiva do Leite",
        "version": "1.3.0-hackweb3-live-spectrometer-capture",
        "created_at": utc_now(),
        "sample": milk_sample,
        "analysis": {
            "status": integrated["status"],
            "compliance_score": integrated["integrated_score"],
            "spectral_consistency": process["milk_analysis"]["spectral_consistency"],
            "water_adulteration_risk": process["milk_analysis"]["water_adulteration_risk"],
            "temperature_risk": process["milk_analysis"]["temperature_risk"],
            "solids_index": process["milk_analysis"]["solids_index"],
            "recommendation": integrated["conclusion"],
        },
        "chain_process": process,
        "web3": {
            "hash_algorithm": "SHA-256",
            "storage_strategy": "off-chain full-chain evidence + on-chain hash",
            "privacy_note": "A blockchain registra o hash da evidência completa; dados sensíveis ficam off-chain.",
            "auditable_scope": ["solo", "alimentação", "água", "leite", "transporte", "análise espectral"],
        },
    }
    payload["evidence_hash"] = sha256_payload(payload)
    return payload



def build_investor_impact_model(
    scenario: str = "normal",
    seed: int | None = 42,
    *,
    monthly_liters: float = 450000,
    milk_price_brl: float = 2.40,
    baseline_loss_pct: float = 0.018,
    loss_reduction_pct: float = 0.42,
    quality_bonus_pct: float = 0.012,
    audits_per_month: int = 24,
    audit_cost_brl: float = 180.0,
    audit_efficiency_gain_pct: float = 0.45,
    hardware_kit_brl: float = 18500.0,
    onboarding_brl: float = 7500.0,
    monthly_saas_brl: float = 1490.0,
    analysis_fee_brl: float = 0.35,
    analyses_per_month: int = 900,
) -> Dict[str, Any]:
    """Modelo demonstrativo de impacto para investidor e cliente.

    O objetivo não é prometer resultado financeiro, mas mostrar a lógica de valor:
    redução de perdas, bônus por rastreabilidade/qualidade, menor custo de auditoria
    e receita recorrente para a Análise Evolutiva.
    """
    process = build_full_chain_process(scenario=scenario, seed=seed)
    integrated = process["integrated_analysis"]
    milk = process["milk_analysis"]

    monthly_revenue_protected = max(monthly_liters, 0) * max(milk_price_brl, 0)
    estimated_loss_without_traceability = monthly_revenue_protected * max(baseline_loss_pct, 0)

    status_factor = {"APROVADO": 1.0, "ATENÇÃO": 0.82, "REPROVADO": 0.55}.get(integrated["status"], 0.75)
    effective_loss_reduction_pct = _bounded(loss_reduction_pct * status_factor, 0, 0.95)
    avoided_loss = estimated_loss_without_traceability * effective_loss_reduction_pct

    quality_bonus = monthly_revenue_protected * max(quality_bonus_pct, 0) if integrated["status"] in {"APROVADO", "ATENÇÃO"} else 0
    audit_savings = max(audits_per_month, 0) * max(audit_cost_brl, 0) * _bounded(audit_efficiency_gain_pct, 0, 1)
    monthly_operational_benefit = avoided_loss + quality_bonus + audit_savings
    annual_operational_benefit = monthly_operational_benefit * 12

    first_year_cost_for_client = max(hardware_kit_brl, 0) + max(onboarding_brl, 0) + max(monthly_saas_brl, 0) * 12 + max(analysis_fee_brl, 0) * max(analyses_per_month, 0) * 12
    payback_months = None if monthly_operational_benefit <= 0 else first_year_cost_for_client / monthly_operational_benefit
    first_year_roi_pct = None if first_year_cost_for_client <= 0 else ((annual_operational_benefit - first_year_cost_for_client) / first_year_cost_for_client) * 100

    vendor_mrr = max(monthly_saas_brl, 0) + max(analysis_fee_brl, 0) * max(analyses_per_month, 0)
    vendor_arr = vendor_mrr * 12
    hardware_margin_proxy = max(hardware_kit_brl, 0) * 0.35

    return {
        "scenario": scenario,
        "scenario_label": process["scenario_label"],
        "process_id": process["process_id"],
        "status": integrated["status"],
        "integrated_score": integrated["integrated_score"],
        "technical_risks": {
            "water_adulteration_risk": milk["water_adulteration_risk"],
            "temperature_risk": milk["temperature_risk"],
            "soil_moisture_risk": process["soil"]["analysis"]["moisture_risk"],
            "feed_risk": process["feed"]["analysis"]["fermentation_or_mold_risk"],
            "water_turbidity_risk": process["water"]["analysis"]["turbidity_risk"],
        },
        "client_value_simulation": {
            "monthly_liters": round(monthly_liters, 2),
            "milk_price_brl": round(milk_price_brl, 2),
            "monthly_revenue_protected_brl": round(monthly_revenue_protected, 2),
            "baseline_loss_pct": round(baseline_loss_pct, 4),
            "estimated_loss_without_traceability_brl": round(estimated_loss_without_traceability, 2),
            "effective_loss_reduction_pct": round(effective_loss_reduction_pct, 4),
            "avoided_loss_brl_month": round(avoided_loss, 2),
            "quality_bonus_brl_month": round(quality_bonus, 2),
            "audit_savings_brl_month": round(audit_savings, 2),
            "monthly_operational_benefit_brl": round(monthly_operational_benefit, 2),
            "annual_operational_benefit_brl": round(annual_operational_benefit, 2),
            "first_year_cost_for_client_brl": round(first_year_cost_for_client, 2),
            "payback_months": None if payback_months is None else round(payback_months, 1),
            "first_year_roi_pct": None if first_year_roi_pct is None else round(first_year_roi_pct, 1),
        },
        "business_model_simulation": {
            "hardware_kit_brl": round(hardware_kit_brl, 2),
            "onboarding_brl": round(onboarding_brl, 2),
            "monthly_saas_brl": round(monthly_saas_brl, 2),
            "analysis_fee_brl": round(analysis_fee_brl, 2),
            "analyses_per_month": analyses_per_month,
            "vendor_mrr_brl_per_client": round(vendor_mrr, 2),
            "vendor_arr_brl_per_client": round(vendor_arr, 2),
            "hardware_margin_proxy_brl": round(hardware_margin_proxy, 2),
            "revenue_streams": [
                "venda/locação do kit espectrofotométrico",
                "assinatura SaaS para dashboards, laudos e rastreabilidade",
                "taxa por análise registrada e evidência verificável",
                "licenciamento para cooperativas, laticínios e laboratórios",
                "contratos de integração com sensores, ERP e auditoria",
            ],
        },
        "investment_thesis": {
            "why_now": [
                "cadeias agroalimentares precisam provar origem, qualidade e integridade dos laudos",
                "hardware óptico reduz dependência de coleta manual e cria dado técnico próprio",
                "Web3 transforma laudos e medições em evidências verificáveis por terceiros",
                "a base histórica de curvas espectrais pode virar ativo defensável de IA",
            ],
            "defensibility": [
                "curvas espectrais calibradas por matriz e região",
                "base proprietária de leite, solo, alimentação, água e histórico de transporte",
                "integração hardware + IA + laudo + blockchain em uma única trilha",
                "relacionamento com cooperativas/laticínios e possibilidade de rede de verificação",
            ],
            "next_milestones": [
                "validar protótipo com amostras reais e curva laboratorial",
                "conectar equipamento físico ESP32/AS7341 ao backend",
                "deploy do smart contract em testnet e geração de QR Code público",
                "piloto com produtor/cooperativa/laticínio e relatório de economia operacional",
                "treinar modelos com histórico de amostras e ampliar para solo, pastagem, alimentação, água e bioinsumos",
            ],
        },
        "process_snapshot": process,
        "disclaimer": "Simulação financeira e técnica para apresentação do MVP. Não representa promessa de retorno; os parâmetros devem ser validados em piloto real.",
    }


def build_demo_evidence(scenario: str = "normal", seed: int | None = 42) -> Dict[str, Any]:
    sample = sample_to_dict(simulate_spectral_reading(scenario=scenario, seed=seed))
    analysis = analyze_milk_sample(sample)
    return build_evidence(sample, analysis)


def build_demo_chain_evidence(scenario: str = "normal", seed: int | None = 42) -> Dict[str, Any]:
    process = build_full_chain_process(scenario=scenario, seed=seed)
    return build_chain_evidence(process)


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


# ---------------------------------------------------------------------------
# Simulador estratégico completo da Análise Evolutiva V11
# ---------------------------------------------------------------------------

def _risk_label(score: float) -> str:
    if score >= 0.78:
        return "baixo"
    if score >= 0.58:
        return "moderado"
    return "alto"


def _severity_label(value: float, low: float, high: float) -> str:
    if value < low:
        return "baixo"
    if value < high:
        return "médio"
    return "alto"


def _simulate_droplet_application(rng: random.Random, scenario: str) -> Dict[str, Any]:
    base_coverage = 0.74 if scenario not in {"integrated_risk", "feed_risk"} else 0.58
    coverage = round(_bounded(base_coverage + rng.uniform(-0.06, 0.06), 0.25, 0.95), 3)
    density = int(72 + coverage * 95 + rng.randint(-12, 16))
    uniformity = round(_bounded(0.92 - abs(coverage - 0.72) * 0.9 + rng.uniform(-0.04, 0.03), 0.35, 0.99), 3)
    drift = round(_bounded((1 - uniformity) * 0.55 + rng.uniform(0.01, 0.08), 0.0, 0.55), 3)
    score = round(_bounded((coverage * 0.45) + (uniformity * 0.40) + ((1 - drift) * 0.15), 0, 1), 3)
    return {
        "module": "Bioinsumos e gotículas",
        "objective": "Calibrar deposição, cobertura e qualidade da aplicação de bioinsumos.",
        "capture": "Imagem RGB/UV de papel hidrossensível ou superfície foliar",
        "metrics": {
            "coverage_pct": round(coverage * 100, 1),
            "droplet_density_per_cm2": density,
            "uniformity_index": uniformity,
            "drift_risk": drift,
            "technical_score": score,
        },
        "classification": _risk_label(score),
        "recommendation": "Ajustar bico/pressão e repetir calibração" if score < 0.70 else "Aplicação dentro da faixa operacional demonstrativa",
        "data_products": ["mapa de cobertura", "histórico por talhão", "alerta de deriva", "relatório de aplicação"],
    }


def _simulate_soil_module(rng: random.Random, scenario: str) -> Dict[str, Any]:
    spectral = simulate_wave_capture(_scenario_adjusted_profile("soil", scenario), scenario, "soil", seed=rng.randint(1, 10_000))
    moisture = round(_bounded(0.34 + rng.uniform(-0.08, 0.06) - (0.10 if scenario in {"soil_moisture_stress", "integrated_risk"} else 0), 0.08, 0.62), 3)
    n = round(38 + rng.uniform(-8, 8) - (7 if scenario in {"soil_moisture_stress", "integrated_risk"} else 0), 1)
    p = round(21 + rng.uniform(-5, 5), 1)
    k = round(118 + rng.uniform(-22, 18), 1)
    ph = round(6.1 + rng.uniform(-0.45, 0.35) - (0.25 if scenario in {"soil_moisture_stress", "integrated_risk"} else 0), 2)
    ece = round(0.52 + rng.uniform(-0.11, 0.18) + (0.24 if scenario in {"soil_moisture_stress", "integrated_risk"} else 0), 2)
    organic_matter = round(2.8 + rng.uniform(-0.6, 0.5), 2)
    score = _bounded((moisture/0.55)*0.24 + (min(n, 45)/45)*0.18 + (min(p, 28)/28)*0.12 + (min(k, 140)/140)*0.16 + (1 - abs(ph-6.2)/2.5)*0.18 + (1 - min(ece, 1.4)/1.8)*0.12, 0, 1)
    return {
        "module": "Solo e pastagem",
        "objective": "Apoiar análise físico-química e indicar risco de umidade, salinidade, fertilidade e matéria orgânica.",
        "capture": "Reflectância UV/VIS/NIR + sensores NPK, pH, umidade e ECe",
        "spectral_capture": spectral,
        "metrics": {
            "moisture_pct": round(moisture * 100, 1),
            "nitrogen_mg_dm3": n,
            "phosphorus_mg_dm3": p,
            "potassium_mg_dm3": k,
            "ph": ph,
            "ece_ds_m": ece,
            "organic_matter_pct": organic_matter,
            "technical_score": round(score, 3),
        },
        "classification": _risk_label(score),
        "recommendation": "Priorizar correção de umidade/salinidade e confirmar em laboratório" if score < 0.65 else "Solo em condição operacional aceitável para o ciclo simulado",
        "data_products": ["score do talhão", "assinatura espectral do solo", "histórico de fertilidade", "alerta de salinização"],
    }


def _simulate_root_and_yield(rng: random.Random, soil: Mapping[str, Any], scenario: str) -> Dict[str, Any]:
    metrics = soil["metrics"]
    vigor = _bounded((metrics["moisture_pct"]/45)*0.26 + (metrics["nitrogen_mg_dm3"]/45)*0.18 + (metrics["phosphorus_mg_dm3"]/28)*0.14 + (metrics["potassium_mg_dm3"]/150)*0.16 + (1 - abs(metrics["ph"]-6.2)/2.3)*0.16 + rng.uniform(-0.04, 0.04), 0, 1)
    vigor_score = round(vigor * 10, 2)
    yield_previous = round(47 + rng.uniform(-5, 4), 1)
    yield_pred = round(yield_previous * (0.93 + vigor * 0.22) - (3.5 if scenario in {"soil_moisture_stress", "integrated_risk"} else 0), 1)
    return {
        "module": "Raiz, vigor e predição de safra/pastagem",
        "objective": "Transformar solo, clima e manejo em previsão operacional para produtividade e suporte alimentar do rebanho.",
        "metrics": {
            "root_vigor_score_0_10": vigor_score,
            "yield_previous_index": yield_previous,
            "yield_predicted_index": yield_pred,
            "expected_delta_pct": round(((yield_pred - yield_previous) / yield_previous) * 100, 1),
            "model_confidence": round(_bounded(0.62 + vigor * 0.26 + rng.uniform(-0.03, 0.04), 0.45, 0.93), 3),
        },
        "classification": _risk_label(vigor),
        "recommendation": "Ajustar irrigação/adubação e acompanhar vigor radicular" if vigor < 0.65 else "Manter manejo e monitorar tendência semanal",
        "data_products": ["score de raiz", "previsão de produção", "alerta por talhão", "relatório de evolução"],
    }


def _simulate_irrigation_roi(rng: random.Random, soil: Mapping[str, Any], root_yield: Mapping[str, Any], scenario: str) -> Dict[str, Any]:
    total_water_mm = 82 if scenario in {"soil_moisture_stress", "integrated_risk"} else 112
    plots = []
    remaining = total_water_mm
    for idx, name in enumerate(["Talhão A", "Talhão B", "Talhão C"]):
        need = round(rng.uniform(24, 44), 1)
        marginal_return = round(rng.uniform(38, 72), 2)
        allocated = round(min(need + rng.uniform(-4, 5), remaining/(3-idx)), 1) if idx < 2 else round(max(0, remaining), 1)
        remaining -= allocated
        plots.append({"plot": name, "minimum_need_mm": need, "allocated_mm": allocated, "marginal_return_brl_per_mm": marginal_return, "estimated_return_brl": round(allocated * marginal_return, 2)})
    total_return = round(sum(p["estimated_return_brl"] for p in plots), 2)
    return {
        "module": "Pesquisa Operacional para irrigação e ROI",
        "objective": "Distribuir água e insumos entre talhões priorizando retorno econômico e redução de risco.",
        "method": "Otimização demonstrativa estilo CPLEX/PuLP com restrição de água total",
        "metrics": {"total_available_water_mm": total_water_mm, "estimated_return_brl": total_return, "water_efficiency_score": round(_bounded(total_return/(total_water_mm*72), 0, 1), 3)},
        "plots": plots,
        "classification": "plano otimizado demonstrativo",
        "recommendation": "Executar alocação recomendada e recalcular após nova leitura de umidade",
        "data_products": ["plano de irrigação", "ROI por talhão", "cenário água escassa", "alerta de restrição"],
    }



def _simulate_reports_and_governance(ecosystem_modules: List[Mapping[str, Any]], scenario: str) -> Dict[str, Any]:
    average_score = round(sum(m.get("metrics", {}).get("technical_score", m.get("metrics", {}).get("water_efficiency_score", 0.72)) for m in ecosystem_modules if isinstance(m.get("metrics"), Mapping)) / max(1, len(ecosystem_modules)), 3)
    return {
        "module": "Dashboards, laudos, governança e documentação automática",
        "objective": "Transformar captura de campo em histórico, indicadores, documentos técnicos e evidências verificáveis.",
        "metrics": {
            "ecosystem_score": average_score,
            "modules_connected": len(ecosystem_modules),
            "alerts_generated": sum(1 for m in ecosystem_modules if m.get("classification") in {"moderado", "alto"}),
            "report_sections": 8,
            "data_lineage_steps": 9,
        },
        "outputs": [
            "dashboard por propriedade/talhão/lote",
            "histórico de amostras e versões de modelos",
            "laudo interpretável com limitações técnicas",
            "trilha de evidência para auditoria Web3",
            "documentação para investidor e piloto",
        ],
        "governance": [
            "dados sintéticos no MVP; calibração real permanece proprietária",
            "validação laboratorial necessária antes de uso comercial",
            "hash registra integridade; dados sensíveis permanecem off-chain",
            "versão do modelo e do firmware ficam registrados na evidência",
        ],
    }


def build_complete_evolutionary_analysis(scenario: str = "normal", seed: int | None = 42) -> Dict[str, Any]:
    """Simula a visão completa da Análise Evolutiva V11, mantendo o leite como caso Web3 central."""
    if scenario not in SCENARIO_LABELS:
        raise ValueError(f"Cenário inválido: {scenario}. Use: {', '.join(SCENARIO_LABELS)}")
    rng = _scenario_rng(seed, scenario, salt=10_001)
    milk_chain = build_full_chain_process(scenario=scenario, seed=seed)
    milk_chain_evidence = build_chain_evidence(milk_chain)
    droplet = _simulate_droplet_application(rng, scenario)
    soil = _simulate_soil_module(rng, scenario)
    root_yield = _simulate_root_and_yield(rng, soil, scenario)
    irrigation = _simulate_irrigation_roi(rng, soil, root_yield, scenario)
    modules = [droplet, soil, root_yield, irrigation]
    governance = _simulate_reports_and_governance(modules, scenario)
    evidence_core = {
        "scenario": scenario,
        "milk_chain_hash": milk_chain_evidence["evidence_hash"],
        "modules": [{"module": m["module"], "classification": m.get("classification"), "metrics": m.get("metrics", {})} for m in modules],
        "firmware": SPECTROMETER_CONFIG["firmware"],
        "created_at": utc_now(),
    }
    ecosystem_hash = sha256_payload(evidence_core)
    investor_impact = build_investor_impact_model(scenario=scenario, seed=seed)
    return {
        "project": "Análise Evolutiva V11 - Ecossistema Agro/FoodTech Web3",
        "scenario": scenario,
        "scenario_label": SCENARIO_LABELS[scenario],
        "thesis": {
            "positioning": "Plataforma de IA óptica aplicada ao agro e aos alimentos, com rastreabilidade Web3 por evidência.",
            "core_problem": "Análises de solo, leite, alimentação, água, pastagem e aplicação de bioinsumos ainda são lentas, caras e pouco integradas ao histórico operacional.",
            "investment_case": "SaaS + hardware + taxa por análise + consultoria técnica, formando base proprietária de dados ópticos por lote.",
            "moat": ["base própria de imagens/espectros", "calibração contra métodos de referência", "histórico por lote", "integração edge/cloud", "trilha Web3 de evidências"],
        },
        "hardware_topology": {
            "edge_devices": ["ESP32", "Raspberry Pi Pico 2W", "ESP32-CAM", "sensor AS7341", "NPK", "pH", "umidade", "ECe"],
            "communication": ["HTTP/REST", "MQTT demonstrativo", "Wi-Fi local", "JSON assinado por lote"],
            "capture_modes": ["imagem RGB/UV", "reflectância", "transmitância", "leitura NPK/pH/umidade/ECe", "metadados de lote"],
        },
        "edge_to_cloud_flow": [
            "captura física por câmera/sensor/espectrofotômetro",
            "pré-processamento no dispositivo ou gateway",
            "envio HTTP/MQTT para backend Flask",
            "extração de features e quimiometria",
            "modelos de IA classificam risco/score",
            "dashboard registra histórico e recomendações",
            "evidência técnica é gerada em JSON canônico",
            "hash SHA-256 é preparado para smart contract",
            "verificação pública comprova integridade sem expor dado sensível",
        ],
        "modules": {
            "bioinsumos_goticulas": droplet,
            "solo_pastagem": soil,
            "raiz_predicao_safra": root_yield,
            "irrigacao_roi": irrigation,
            "leite_web3": {
                "module": "Leite e rastreabilidade Web3",
                "objective": "Análise fotométrica/espectral, controle da cadeia fria, detecção de risco e evidência verificável.",
                "milk_sample": milk_chain["milk_sample"],
                "integrated_analysis": milk_chain["integrated_analysis"],
                "spectrophotometer_session": milk_chain["spectrophotometer_session"],
                "evidence_preview": {"hash": milk_chain_evidence["evidence_hash"], "evidence_id": milk_chain_evidence["evidence_id"]},
            },
            "dashboards_governanca": governance,
        },
        "web3_layer": {
            "strategy": "off-chain para dados completos e on-chain para hash, status, versão e auditoria",
            "ecosystem_evidence_hash": ecosystem_hash,
            "milk_chain_evidence_hash": milk_chain_evidence["evidence_hash"],
            "smart_contract": "AnaliseEvolutivaLeiteTrace.sol",
            "privacy_note": "O MVP não publica dados sensíveis em blockchain; publica apenas prova de integridade.",
        },
        "investor_impact": investor_impact,
        "roadmap_to_product": [
            "piloto controlado com cooperativa/laticínio",
            "coleta pareada com método laboratorial de referência",
            "curvas de calibração por matriz e região",
            "validação metrológica do protótipo óptico",
            "painel multiusuário SaaS",
            "registro Web3 em testnet/mainnet conforme custo e governança",
        ],
    }


def build_complete_ecosystem_evidence(ecosystem: Mapping[str, Any]) -> Dict[str, Any]:
    payload = {
        "project": ecosystem.get("project"),
        "scenario": ecosystem.get("scenario"),
        "scenario_label": ecosystem.get("scenario_label"),
        "web3_layer": ecosystem.get("web3_layer"),
        "modules_summary": {
            key: {
                "module": value.get("module") if isinstance(value, Mapping) else key,
                "classification": value.get("classification") if isinstance(value, Mapping) else None,
                "metrics": value.get("metrics", {}) if isinstance(value, Mapping) else {},
            }
            for key, value in dict(ecosystem.get("modules", {})).items()
        },
        "created_at": utc_now(),
    }
    return {
        "evidence_id": f"AE-ECO-{uuid.uuid4().hex[:12].upper()}",
        "evidence_type": "complete_ecosystem_simulation",
        "created_at": payload["created_at"],
        "sample": {
            "batch_id": f"AE-ECO-{ecosystem.get('scenario', 'normal')}",
            "producer_id": "AE-PLATFORM-V11",
            "producer_name": "Análise Evolutiva",
        },
        "analysis": {
            "status": "ECOSSISTEMA_SIMULADO",
            "compliance_score": payload.get("web3_layer", {}).get("ecosystem_evidence_hash", "")[:8],
            "recommendation": "Evidência demonstrativa do ecossistema completo para avaliação técnica e investimento.",
        },
        "payload": payload,
        "hash": sha256_payload(payload),
        "evidence_hash": sha256_payload(payload),
        "integrity_algorithm": "SHA-256 over canonical JSON",
        "license_note": "MVP demonstrativo com dados sintéticos; calibração real, bases laboratoriais e modelos proprietários não estão incluídos.",
    }



def build_milk_chain_use_cases() -> Dict[str, Any]:
    """Casos de uso comerciais da Análise Evolutiva para a cadeia do leite.

    Estes dados representam a camada de produto/mercado que conecta a captura
    espectrofotométrica, a análise técnica e a rastreabilidade Web3 aos desafios
    reais de produtores, cooperativas, laticínios, distribuidores e investidores.
    """
    cases = [
        {
            "id": "a2a2",
            "label": "A2A2",
            "title": "Leite A2A2 Certificado",
            "description": "Detecção de assinatura proteica A2A2 por espectroscopia e análise comparativa da amostra. O fluxo gera certificação de origem, trilha desde a ordenha e evidência digital para agregação de valor.",
            "technical_signal": ["proteina_a2a2", "assinatura_espectral", "origem_do_lote", "historico_de_ordenha"],
            "web3_value": "Hash do laudo e dos metadados do lote para prova de integridade da certificação.",
            "impact": "Acesso a mercado premium e diferencial de marca, com potencial de agregação de valor de até 40% no preço percebido.",
            "investor_angle": "Produto premium com maior margem, recorrência por certificação e expansão para selos de qualidade.",
            "expected_gain_pct": 0.40,
        },
        {
            "id": "organico",
            "label": "Orgânico",
            "title": "Leite de Propriedade Orgânica",
            "description": "Rastreamento da alimentação, histórico de pastagem, conformidade produtiva e coerência entre solo, água, manejo e leite analisado.",
            "technical_signal": ["solo_pastagem", "alimentacao", "agua", "leite", "conformidade_organica"],
            "web3_value": "Prova de origem, histórico de conformidade e trilha auditável para certificação orgânica.",
            "impact": "Certificação comprovada e valorização comercial de até 35% em canais de maior valor agregado.",
            "investor_angle": "Vertical de certificação contínua, com assinatura SaaS, taxa por auditoria e base histórica do produtor.",
            "expected_gain_pct": 0.35,
        },
        {
            "id": "raca",
            "label": "Raça",
            "title": "Leite de Raça Específica",
            "description": "Identificação de assinatura espectral associada a Jersey, Holandesa, Girolando, Guernsey ou composição específica do rebanho, cruzando proteína, gordura, composição e origem.",
            "technical_signal": ["assinatura_espectral", "perfil_proteico", "perfil_lipidico", "origem_do_rebanho"],
            "web3_value": "Rastreabilidade por raça, lote e propriedade, com prova de integridade do histórico produtivo.",
            "impact": "Diferenciação no mercado e potencial de agregação de valor de até 30%.",
            "investor_angle": "Segmentação premium e criação de produtos rastreados por identidade produtiva.",
            "expected_gain_pct": 0.30,
        },
        {
            "id": "fraude",
            "label": "Fraude",
            "title": "Detecção de Fraude",
            "description": "Identificação de leite em pó adulterado, água adicionada, mistura com leite de outra origem e inconsistências na assinatura espectral do lote.",
            "technical_signal": ["agua_adicionada", "solidos_totais", "perfil_uv_vis_nir", "inconsistencia_de_origem"],
            "web3_value": "Blockchain registra a evidência, impedindo alteração posterior do laudo e fortalecendo a cadeia de custódia.",
            "impact": "Elimina fraude, protege marca e fortalece conformidade auditável.",
            "investor_angle": "Economia direta por perdas evitadas, seguro de qualidade e redução de contestação comercial.",
            "expected_gain_pct": None,
        },
        {
            "id": "contaminacao",
            "label": "Contaminação",
            "title": "Rastreamento de Contaminação",
            "description": "Detecção precoce de contaminantes, patógenos indicativos, resíduos ou alteração físico-química por leitura espectral e correlação com água, alimentação e transporte.",
            "technical_signal": ["turbidez", "temperatura", "agua", "residuos", "anomalia_espectral"],
            "web3_value": "Histórico imutável para isolamento rápido de lotes comprometidos e auditoria sanitária.",
            "impact": "Redução de desperdício de até 25%, segurança alimentar e menor tempo de resposta.",
            "investor_angle": "Valor operacional alto para cooperativas e laticínios por reduzir descarte amplo e preservar lotes saudáveis.",
            "expected_loss_reduction_pct": 0.25,
        },
        {
            "id": "lote",
            "label": "Lote",
            "title": "Rastreabilidade de Lote",
            "description": "Histórico completo de origem, propriedade, data, temperatura, transporte, análise espectrofotométrica, status técnico e QR Code público para verificação pelo consumidor ou auditor.",
            "technical_signal": ["origem", "propriedade", "temperatura", "transporte", "hash_do_laudo", "qr_code"],
            "web3_value": "Camada de verificação pública baseada em hash, status e timestamp do smart contract.",
            "impact": "Transparência total, confiança do consumidor e redução de risco reputacional.",
            "investor_angle": "Base para produto SaaS multiagente: produtor, laboratório, cooperativa, laticínio, fiscalização e varejo.",
            "expected_gain_pct": None,
        },
    ]
    return {
        "project": "Análise Evolutiva Web3 — Cadeia Produtiva do Leite",
        "source": "Camada de casos de uso comerciais extraída do posicionamento institucional da Análise Evolutiva.",
        "summary": "Soluções específicas para A2A2, orgânico, raça, fraude, contaminação e rastreabilidade de lote, conectadas à espectrofotometria, IA e Web3.",
        "cases": cases,
        "platform_fit": {
            "spectrophotometer": "Captura UV/VIS/NIR, corrente escura, branco/referência, ADC, sinal normalizado e absorbância.",
            "ai_layer": "Classificação de conformidade, risco de fraude, risco sanitário, coerência de origem e score técnico.",
            "web3_layer": "Registro de hash, status, timestamp e trilha de auditoria sem expor dados sensíveis da propriedade.",
            "business_layer": "SaaS, taxa por análise, kit óptico, certificação, auditoria e licenciamento para cooperativas/laticínios.",
        },
        "investor_message": "O MVP deixa de ser apenas uma simulação técnica e passa a demonstrar produtos vendáveis com Web3: certificação premium, prevenção de fraude, rastreabilidade de lote e auditoria de qualidade com receita recorrente.",
    }
