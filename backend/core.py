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
    return {
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
        "version": "1.2.0-hackweb3-spectrometer-simulator",
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
        "version": "1.2.0-hackweb3-spectrometer-simulator",
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
